from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models, transaction, IntegrityError


class UserQuerySet(models.QuerySet):
    def medics(self):
        return self.exclude(medic__isnull=True)

    def patients(self):
        return self.exclude(patient__isnull=True)


class MedicManager(models.Manager):
    def _fixed_license(self, license):
        if license is not None:
            license = license.strip() if license.strip() != '' else None
        return license

    def create(self, user, license):
        return super().create(user=user, license=self._fixed_license(license))


class UserManager(DjangoUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _fixed_license(self, license):
        if license is not None:
            license = license.strip() if license.strip() != '' else None
        return license

    def create_user(self, username, license=None, current_medic=None, **kwargs):
        with transaction.atomic():
            user = super().create_user(username,  **kwargs)
            if license is not None:
                Medic.objects.create(user=user, license=license)
            else:
                Patient.objects.create(user=user, current_medic=current_medic)
        return user

    def patients(self):
        return self.get_queryset().patients()

    def medics(self):
        return self.get_queryset().medics()


class User(AbstractUser):
    # FIXME Sacar null true cuando el ISSUE 93 este terminado
    id_google = models.CharField(max_length=100, db_index=True, null=True, blank=True, default=None)

    objects = UserManager()

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


class Medic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license = models.CharField(max_length=100)

    objects = MedicManager()


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    current_medic = models.ForeignKey(User, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)
