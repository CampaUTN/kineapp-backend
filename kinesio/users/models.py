# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserType(models.Model):
    pass


class Medic(CustomUserType):
    license = models.CharField(max_length=100)


class Patient(CustomUserType):
    current_medic = models.ForeignKey(Medic, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)


class CustomUser(AbstractUser):
    user_type = models.OneToOneField(CustomUserType, parent_link=True, related_name='user', on_delete=models.CASCADE)

