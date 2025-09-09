import base64
import json
import os
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import CustomUser
import google.generativeai as genai
from .models import SentEmail
import traceback

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class GmailLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.REDIRECT_URI],
                }
            },
            scopes=[
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/gmail.readonly",
                "openid"
            ]
        )
        flow.redirect_uri = settings.REDIRECT_URI
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        request.session['oauth_flow_state'] = state
        return redirect(auth_url)


class GmailCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        state = request.session.get("oauth_flow_state")
        if not state:
            return Response({"error": "Missing state"}, status=400)

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.REDIRECT_URI],
                }
            },
            scopes=[
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/gmail.readonly",
                "openid"
            ],
            state=state
        )
        flow.redirect_uri = settings.REDIRECT_URI

        try:
            flow.fetch_token(authorization_response=request.build_absolute_uri())
        except Exception as e:
            return Response({"error": f"Token fetch failed: {str(e)}"}, status=400)

        credentials = flow.credentials
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        email = user_info.get("email")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0] + "_" + str(uuid.uuid4())[:8]
            }
        )

        user.gmail_token = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        user.set_unusable_password()
        user.save()

        refresh = RefreshToken.for_user(user)
        response = redirect("http://localhost:3000/send")
        response.set_cookie("access_token", str(refresh.access_token), samesite="Lax")
        response.set_cookie("refresh_token", str(refresh), httponly=True, samesite="Lax")
        return response


class GmailSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        message = request.data.get("message")
        recipient_email = request.data.get("recipient_email")
        image = request.FILES.get("image")

        print("🔐 Is user authenticated?", user.is_authenticated)
        print("👤 User:", user.email)
        print("🧠 Token:", user.gmail_token)

        if not user.gmail_token:
            return Response({"error": "Missing Gmail token"}, status=400)

        # Step 1: Generate corrected message and subject using Gemini
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")

            corrected = model.generate_content(f"Correct the grammar of this email message:\n\n{message}")
            corrected_message = corrected.text.strip()

            subject_response = model.generate_content(
                f"Generate only one short and professional email subject line (less than 10 words). Do not include any explanation.\n\nMessage:\n{corrected_message}"
            )
            subject = subject_response.text.strip().split('\n')[0]

        except Exception as e:
            print("❌ Gemini Error:", str(e))
            traceback.print_exc()
            corrected_message = message
            subject = "No Subject"

        # Step 2: Save uploaded image and convert to PDF
        try:
            pdf_id = str(uuid.uuid4())
            image_name = f"{pdf_id}.png"
            image_path = os.path.join(settings.MEDIA_ROOT, image_name)

            with open(image_path, "wb") as f:
                f.write(image.read())

            pdf_path = os.path.join(settings.MEDIA_ROOT, f"{pdf_id}.pdf")
            c = canvas.Canvas(pdf_path, pagesize=letter)
            image_path = os.path.normpath(image_path).replace("\\", "/")
            c.drawImage(image_path, 100, 400, width=400, height=300)
            c.save()
        except Exception as e:
            print("❌ PDF Generation Error:", str(e))
            traceback.print_exc()
            return Response({"error": f"PDF generation error: {str(e)}"}, status=500)

        # Step 3: Send email via Gmail API
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            creds = Credentials(
                token=user.gmail_token['token'],
                refresh_token=user.gmail_token['refresh_token'],
                token_uri=user.gmail_token['token_uri'],
                client_id=user.gmail_token['client_id'],
                client_secret=user.gmail_token['client_secret'],
                scopes=user.gmail_token['scopes']
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())

            service = build('gmail', 'v1', credentials=creds)

            msg = MIMEMultipart()
            msg['to'] = recipient_email
            if 'from' in msg:
                del msg['from']
            msg['subject'] = subject
            msg.attach(MIMEText(corrected_message, 'plain'))

            with open(pdf_path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype='pdf')
                part.add_header('Content-Disposition', 'attachment', filename=f"{pdf_id}.pdf")
                msg.attach(part)

            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            send_message = {'raw': raw_message}
            service.users().messages().send(userId="me", body=send_message).execute()

            # Save to MongoDB
            from pymongo import MongoClient
            from datetime import datetime

            client = MongoClient("mongodb+srv://meghana70132:1234@cluster0.ru8caxy.mongodb.net/smart_messenger?retryWrites=true&w=majority")
            db = client["smart_messenger"]
            collection = db["sentemails"]
            print("📤 Storing to MongoDB:")
            print("Sender:", user.email)
            print("Recipient:", recipient_email)
            print("Subject:", subject)
            print("Message:", message)
            print("Corrected Message:", corrected_message)
            print("PDF Path:", pdf_path)


            collection.insert_one({
                "sender": user.email,
                "recipient": recipient_email,
                "subject": subject,
                "message": message,
                "corrected_message": corrected_message,
                "timestamp": datetime.now(),
                "file_path": str(pdf_path),
            })

            return Response({
                "status": "Email sent",
                "subject": subject,
                "corrected_message": corrected_message,
                "pdf_id": pdf_id
            })

        except Exception as e:
            print("❌ Email Sending Error:", str(e))
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
def build_credentials(token_data):
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes'],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


@csrf_exempt
def generate_subject(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(
                [f"Generate only one short and professional email subject line (less than 10 words). Do not include any explanation.\n\nMessage:\n{message}"]
            )
            subject = response.text.strip().split('\n')[0]
            return JsonResponse({'subject': subject})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=400)