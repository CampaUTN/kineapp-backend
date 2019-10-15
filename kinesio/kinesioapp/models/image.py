from __future__ import annotations
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
from typing import List
from django.db.models.functions import Substr, Lower

from kinesioapp import choices
from users.models import User
from kinesioapp.utils.thumbnail import ThumbnailGenerator
from kinesioapp.utils.models_mixins import CanViewModelMixin
from .clinical_session import ClinicalSession


class ImageQuerySet(models.QuerySet):
    def create(self, content_as_base64: bytes, **kwargs) -> models.Model:
        content_as_base64 = content_as_base64.replace(b'\\n', b'').replace(b'\n', b'')  # to fix a bug in the mobile front end.
        encrypted_content = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(content_as_base64)
        encrypted_thumbnail = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(ThumbnailGenerator(content_as_base64).thumbnail)
        return super().create(_content_base64_and_encrypted=encrypted_content,
                              _thumbnail_base64_and_encrypted=encrypted_thumbnail,
                              **kwargs)

    def by_tag(self, tag: str) -> models.QuerySet:
        return self.annotate(tag_initial=Lower(Substr('tag', 1, 1))).filter(tag_initial=tag[0].lower())

    def of_patient(self, user: User) -> models.QuerySet:
        return self.filter(clinical_session__patient__id__in=user.related_patients.values('id'))

    def has_images_with_tag(self, tag: str) -> bool:
        return self.by_tag(tag).exists()

    def classified_by_tag(self) -> List[dict]:
        return [{'tag': tag, 'images': self.by_tag(tag)} for tag in choices.images.TAGS if self.has_images_with_tag(tag)]


class Image(models.Model, CanViewModelMixin):
    _content_base64_and_encrypted = models.BinaryField()
    _thumbnail_base64_and_encrypted = models.BinaryField()
    clinical_session = models.ForeignKey(ClinicalSession, on_delete=models.CASCADE, null=True, related_name='images')
    tag = models.CharField(max_length=20, choices=choices.images.get())

    objects = ImageQuerySet.as_manager()

    def _decrypted_binary_field(self, field) -> str:
        field = field.tobytes() if type(field) is not bytes else field
        return str(Fernet(settings.IMAGE_ENCRYPTION_KEY).decrypt(field))[2:-1]

    @property
    def content_as_base64(self) -> str:
        return self._decrypted_binary_field(self._content_base64_and_encrypted)

    @property
    def thumbnail_as_base64(self) -> str:
        return self._decrypted_binary_field(self._thumbnail_base64_and_encrypted)

    def can_edit_and_delete(self, user: User) -> bool:
        return self.clinical_session.can_edit_and_delete(user)
