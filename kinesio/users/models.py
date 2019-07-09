from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models, transaction


class CustomUserQuerySet(models.QuerySet):
    def medics(self):
        return self.filter(user_type__in=Medic.objects.all())

    def patients(self):
        return self.filter(user_type__in=Patient.objects.all())


class CustomUserManager(UserManager):
    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db)

    def _fixed_license(self, license):
        if license is not None:
            license = license.strip() if license.strip() != '' else None
        return license

    def create_user(self, username, email=None, password=None, license=None, current_medic=None, **kwargs):
        """ Creates the user including its type (CustomUserType) """
        license = self._fixed_license(license)
        with transaction.atomic():
            user_type = Medic.objects.create(license=license) if license is not None else Patient.objects.create(current_medic=current_medic)
            return super().create_user(username, email, password,  **dict(**kwargs, user_type=user_type))

    def medics(self):
        return self.get_queryset().medics()

    def patients(self):
        return self.get_queryset().patients()


class CustomUserType(models.Model):
    """ We need this class as we can not have the FK 'user_type' of user class pointing to two different tables
        (Patient and medic). """
    pass


class CustomUser(AbstractUser):
    user_type = models.OneToOneField(CustomUserType, parent_link=True, related_name='user', on_delete=models.CASCADE)

    objects = CustomUserManager()


class Medic(CustomUserType):
    license = models.CharField(max_length=100)


class Patient(CustomUserType):
    current_medic = models.ForeignKey(CustomUser, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)
