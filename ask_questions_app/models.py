from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    source = models.CharField(max_length=20)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_text}: {self.source}"

class AccessToken(models.Model):
    token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"AccessToken(token={self.token}, expires_at={self.expires_at})"