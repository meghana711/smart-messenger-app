from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.conf import settings
import mongoengine as me


class Message(models.Model):
    user = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.timestamp}"
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gmail_token = models.JSONField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
class SentEmail(models.Model):
    sender = models.EmailField()
    recipient = models.EmailField()
    subject = models.TextField()
    message = models.TextField()
    corrected_message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'api'