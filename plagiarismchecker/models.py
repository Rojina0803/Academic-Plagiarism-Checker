from django.db import models
from django.contrib.auth.models import User


class StoredDocument(models.Model):

    RISK_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    plagiarism_score = models.FloatField(default=0)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    filename = models.CharField(
        max_length=255
    )

    content = models.TextField()

    overall_similarity_score = models.FloatField(
        default=0
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RISK_CHOICES,
        default='low'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.filename