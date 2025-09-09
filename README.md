Smart Messenger App is a full-stack web application that allows users to send emails from their Gmail account with AI-powered features. Users can upload images, generate subjects using AI, convert images to PDFs, and send emails—all securely via Gmail OAuth.

Features

Gmail OAuth Login: Authenticate securely with your Gmail account.

AI Subject Generation: Automatically generate email subjects using OpenAI Gemini.

Multi-file Upload: Upload images or files, which can be converted to PDF attachments.

Send Emails: Send emails directly from your Gmail account.

Save Sent Emails: Sent emails are stored in MongoDB Atlas.

Dashboard: View sent emails with details like timestamp, receiver, and attachments.

Dark Mode UI: Modern and responsive design.

Tech Stack

Frontend: React, HTML, CSS

Backend: Python Django 4.2

Database: MongoDB Atlas (for sent emails), Django default DB for users

APIs & Libraries: Gmail API (OAuth 2.0), OpenAI Gemini API, ReportLab (PDF generation)

Installation

Clone the repository

git clone https://github.com/<your-username>/smart-messenger-app.git
cd smart-messenger-app


Backend Setup

cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Frontend Setup

cd frontend
npm install
npm start


Environment Variables
Create a .env file in the backend folder with the following:

GMAIL_CLIENT_ID=<your-gmail-client-id>
GMAIL_CLIENT_SECRET=<your-gmail-client-secret>
OPENAI_API_KEY=<your-openai-api-key>
MONGODB_URI=<your-mongodb-uri>


Run Backend

python manage.py migrate
python manage.py runserver

Usage

Open the app in your browser: http://localhost:3000

Log in using your Gmail account.

Enter a message and upload image(s).

Let AI generate a subject or input your own.

Send the email and view it in the dashboard.

Contribution

Contributions are welcome! Please fork the repository and create a pull request.

License
