# api/urls.py

from django.urls import path
from .views import (
    GmailLoginView,
    GmailCallbackView,
    GmailSendView,
    generate_subject,
)

urlpatterns = [
    path('google/login/', GmailLoginView.as_view(), name='google-login'),
    path('google/callback/', GmailCallbackView.as_view(), name='google-callback'),
    path('send-email/', GmailSendView.as_view(), name='send-email'),
    path('generate-subject/', generate_subject, name='generate-subject'),
]


