from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    source = models.CharField(max_length=20)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_text}: {self.source}"