from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models, transaction
from django.conf import settings
from rest_framework.authtoken.models import Token

from kinesioapp.utils.models_mixins import CanViewModelMixin
from users.models.question import SecretQuestion


class UserQuerySet(models.QuerySet):
    def medics(self) -> models.QuerySet:
        return self.exclude(medic__isnull=True)

    def patients(self) -> models.QuerySet:
        return self.exclude(patient__isnull=True)

    def accessible_by(self, user) -> models.QuerySet:
        users_with_access = user.related_patients
        users_with_access |= User.objects.filter(id=user.related_medic.id)
        return self.intersection(users_with_access)


class UserManager(DjangoUserManager):
    def get_queryset(self) -> models.QuerySet:
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, username: str, license: str = None, current_medic: str = None, **kwargs) -> models.Model:
        # We need to use dynamic imports to avoid circular imports.
        from users.models.patient import Patient
        from users.models.medic import Medic
        with transaction.atomic():
            user = super().create_user(username,  **kwargs)
            if license is not None:
                Medic.objects.create(pk=user.pk, id=user.id, user=user, license=license)
            else:
                Patient.objects.create(pk=user.pk, id=user.id, user=user, current_medic=current_medic)
        return user

    def patients(self) -> models.QuerySet:
        return self.get_queryset().patients()

    def medics(self) -> models.QuerySet:
        return self.get_queryset().medics()

    def accessible_by(self, user) -> models.QuerySet:
        return self.get_queryset().accessible_by(user)


class User(AbstractUser, CanViewModelMixin):
    secret_question = models.ForeignKey(SecretQuestion, null=True, on_delete=models.SET_NULL)
    tries = models.IntegerField(default=0)
    picture_url = models.CharField(max_length=255, default=None, null=True)
    dni = models.PositiveIntegerField(unique=True)  # National Identity Document of Argentina
    birth_date = models.DateField()

    objects = UserManager()

    @property
    def is_patient(self):
        return hasattr(self, 'patient')

    @property
    def is_medic(self):
        return not self.is_patient

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

    @property
    def related_medic(self):
        return self.type.related_medic

    def get_or_create_token(self):
        return Token.objects.get_or_create(user=self)[0]

    def __str__(self):
        return f'{"Dr." if self.is_medic else "Pac."} {self.last_name}, {self.first_name}'

    def log_valid_try(self):
        self.tries = 0
        self.save()

    def log_invalid_try(self):
        self.tries += 1
        if self.tries >= settings.MAX_PASSWORD_TRIES:
            self.is_active = False
        self.save()

    def can_edit_and_delete(self, user) -> bool:
        return self == user

    def check_question_and_answer(self, secret_question_id, answer):
        credentials_are_valid = (self.secret_question.id == secret_question_id) and self.check_password(raw_password=answer)
        if not credentials_are_valid:
            self.log_invalid_try()
        else:
            self.log_valid_try()
        return credentials_are_valid
