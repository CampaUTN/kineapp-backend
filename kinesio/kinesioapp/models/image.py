from __future__ import annotations
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
from typing import List
from django.db.models.functions import Substr, Lower

from .. import choices
from users.models import User
from ..utils.thumbnail import ThumbnailGenerator
from ..utils.models_mixins import CanViewModelMixin
from .clinical_session import ClinicalSession
from ..utils.binary_field_to_string import binary_field_to_string


class ImageQuerySet(models.QuerySet):
    def create(self, content_as_base64: bytes, **kwargs) -> models.Model:
        # Replace '\n's to fix a bug in the mobile front end.
        content_as_base64 = content_as_base64.replace(b'\\n', b'').replace(b'\n', b'')
        encrypted_content = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(content_as_base64)
        encrypted_thumbnail = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(ThumbnailGenerator(content_as_base64).thumbnail)
        return super().create(_content_base64_and_encrypted=encrypted_content,
                              _thumbnail_base64_and_encrypted=encrypted_thumbnail,
                              **kwargs)

    def by_tag(self, tag: str) -> ImageQuerySet:
        return self.annotate(tag_initial=Lower(Substr('tag', 1, 1))).filter(tag_initial=tag[0].lower()) if tag else self

    def of_patient(self, user: User) -> ImageQuerySet:
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

    @property
    def content_as_base64(self) -> str:
        return binary_field_to_string(self._content_base64_and_encrypted, decrypt=True)

    @property
    def thumbnail_as_base64(self) -> str:
        return binary_field_to_string(self._thumbnail_base64_and_encrypted, decrypt=True)

    def can_edit_and_delete(self, user: User) -> bool:
        return self.clinical_session.can_edit_and_delete(user)

    def can_view(self, user: User) -> bool:
        return self.clinical_session.can_view(user)
