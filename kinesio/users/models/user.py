from __future__ import annotations
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models, transaction
from django.conf import settings
from rest_framework.authtoken.models import Token
from typing import Optional, Union

from kinesioapp.utils.models_mixins import CanViewModelMixin
from users.models.question import SecretQuestion
from kinesioapp.utils.binary_field_to_string import binary_field_to_string


class UserQuerySet(models.QuerySet):
    def medics(self) -> UserQuerySet:
        return self.exclude(medic__isnull=True)

    def patients(self) -> UserQuerySet:
        return self.exclude(patient__isnull=True)

    def accessible_by(self, user: User) -> UserQuerySet:
        users_with_access = user.related_patients
        users_with_access |= User.objects.filter(id=user.related_medic.id)
        return self.intersection(users_with_access)


class UserManager(DjangoUserManager):
    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, username: str, license: Optional[str] = None, current_medic: Optional[str] = None, **kwargs: dict) -> User:
        # We need to use dynamic imports to avoid circular imports.
        from users.models.patient import Patient
        from users.models.medic import Medic

        # Create the user and its type on a single transaction
        with transaction.atomic():
            user = super().create_user(username, **kwargs)
            if license is not None:
                Medic.objects.create(pk=user.pk, id=user.id, user=user, license=license)
            else:
                Patient.objects.create(pk=user.pk, id=user.id, user=user, current_medic=current_medic)
        return user

    def patients(self) -> UserQuerySet:
        return self.get_queryset().patients()

    def medics(self) -> UserQuerySet:
        return self.get_queryset().medics()

    def accessible_by(self, user: User) -> UserQuerySet:
        return self.get_queryset().accessible_by(user)


class User(AbstractUser, CanViewModelMixin):
    secret_question = models.ForeignKey(SecretQuestion, null=True, on_delete=models.SET_NULL)
    tries = models.PositiveSmallIntegerField(default=0)
    _picture_base64 = models.BinaryField(default=None, null=True)
    dni = models.PositiveIntegerField(unique=True)  # National Identity Document of Argentina
    birth_date = models.DateField()

    objects = UserManager()

    @property
    def picture_base64(self):
        return binary_field_to_string(self._picture_base64)

    @property
    def is_patient(self) -> bool:
        """ Do not use this for type testing. This is intended only to know the user type in the front end. """
        return hasattr(self, 'patient')

    @property
    def is_medic(self) -> bool:
        """ Do not use this for type testing. This is intended only to know the user type in the front end. """
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
    def related_patients(self) -> User:
        return self.type.related_patients

    @property
    def related_medic(self) -> User:
        return self.type.related_medic

    def get_or_create_token(self) -> Token:
        return Token.objects.get_or_create(user=self)[0]

    def __str__(self) -> str:
        return f'{"Dr." if self.is_medic else "Pac."} {self.last_name}, {self.first_name}'

    def log_valid_try(self) -> None:
        self.tries = 0
        self.save()

    def log_invalid_try(self) -> None:
        self.tries += 1
        if self.tries >= settings.MAX_PASSWORD_TRIES:
            self.is_active = False
        self.save()

    def can_edit_and_delete(self, user: User) -> bool:
        return self == user

    def check_question_and_answer(self, secret_question_id: int, answer: str) -> bool:
        credentials_are_valid = self.check_secret_question(secret_question_id) and self.check_password(raw_password=answer)
        if not credentials_are_valid:
            self.log_invalid_try()
        else:
            self.log_valid_try()
        return credentials_are_valid

    def check_secret_question(self, secret_question_id: int) -> bool:
        return self.secret_question.id == secret_question_id

    def check_password(self, raw_password: str) -> bool:
        return super().check_password(raw_password=raw_password.lower())

    def change_profile_picture(self, picture_base64: Union[bytes, str]) -> None:
        if type(picture_base64) is str:
            picture_base64 = bytes(picture_base64.encode('utf-8'))
        self._picture_base64 = picture_base64
        self.save()

    def save(self, **kwargs: dict) -> None:
        # Replace '\n's to fix a bug in the mobile front end.
        if self._picture_base64:
            picture = self._picture_base64.tobytes() if type(self._picture_base64) is not bytes else self._picture_base64
            self._picture_base64 = picture.replace(b'\\n', b'').replace(b'\n',  b'')

        super().save(**kwargs)

    def set_password(self, raw_password: str) -> None:
        # It's a secret answer's response, not a password.
        # Therefore, it should be case insensitive.
        super().set_password(raw_password=raw_password.lower())
