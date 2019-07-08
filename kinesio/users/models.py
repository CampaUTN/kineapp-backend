# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager
from django.db import models
from django.db import transaction


class CustomUserManager(UserManager):
    def _fixed_license(self, license):
        if license is not None:
            license = license.strip() if license.strip() != '' else None
        return license

    def create_user(self, username, email=None, password=None, license=None, current_medic=None, **kwargs):
        license = self._fixed_license(license)
        with transaction.atomic():
            user_type = Medic.objects.create(license=license) if license is not None else Patient.objects.create(current_medic=current_medic)
            return super().create_user(username, email, password,  **dict(**kwargs, user_type=user_type))


class CustomUserType(models.Model):
    pass


class CustomUser(AbstractUser):
    user_type = models.OneToOneField(CustomUserType, parent_link=True, related_name='user', on_delete=models.CASCADE)

    objects = CustomUserManager()


class Medic(CustomUserType):
    license = models.CharField(max_length=100)


class Patient(CustomUserType):
    current_medic = models.ForeignKey(CustomUser, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)




