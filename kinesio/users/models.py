from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models, transaction


class SecretQuestion(models.Model):
    description = models.CharField(max_length=255)


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
    secret_question = models.ForeignKey(SecretQuestion, null=True, on_delete=models.SET_NULL)
    tries = models.IntegerField(default=0)

    objects = UserManager()

    @property
    def is_patient(self):
        try:
            self.patient
            return True
        except Patient.DoesNotExist:
            return False

    @property
    def is_medic(self):
        # We can not do "return not self.is_patient" because during the first save, the user doesn't have a type.
        try:
            self.medic
            return True
        except Medic.DoesNotExist:
            return False

    @property
    def type(self):
        if self.is_patient:
            return self.patient
        elif self.is_medic:
            return self.medic
        else:
            return None

    @property
    def related_patients(self):
        return self.type.related_patients

    def __str__(self):
        return f'{"Dr." if self.is_medic else "Pac."} {self.last_name}, {self.first_name}'


class Medic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license = models.CharField(max_length=100)

    objects = MedicManager()

    @property
    def related_patients(self) -> [User]:
        return [patient.user for patient in self.user.patients.all()]


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    current_medic = models.ForeignKey(User, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)

    @property
    def related_patients(self) -> [User]:
        return [self.user]
