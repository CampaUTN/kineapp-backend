from django.db import models


class SecretQuestion(models.Model):
    description = models.CharField(max_length=255)
