from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
from typing import List

from kinesioapp import choices
from users.models import User, Patient
from kinesioapp.utils.thumbnail import ThumbnailGenerator


class Homework(models.Model):
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    periodicity = models.IntegerField()


class HomeworkExercise(models.Model):
    HOMEWORK_SESSION_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('D', 'DONE'),
        ('C', 'CANCELLED')
    ]

    date = models.DateTimeField()
    number_of_homework_session = models.IntegerField()
    status = models.CharField(max_length=100, choices=HOMEWORK_SESSION_STATUS_CHOICES, default='PENDING')
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, null=True)


class VideoQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(owner=user.related_medic)


class Video(models.Model):
    name = models.CharField(max_length=255)
    content = models.BinaryField()
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    objects = VideoQuerySet.as_manager()


class ClinicalSessionQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(patient__user__in=user.related_patients)


class ClinicalSession(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=choices.sessions.get(), default=choices.sessions.PENDING)
    # Fixme: uncomment when necessary: homework = models.OneToOneField(Homework, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(Patient, related_name='sessions', on_delete=models.CASCADE)

    objects = ClinicalSessionQuerySet.as_manager()

    def can_access(self, user: User) -> bool:
        return self.patient.user in user.related_patients


class ImageQuerySet(models.QuerySet):
    def create(self, content: bytes, **kwargs):
        encrypted_content = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(content)
        encrypted_thumbnail = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(ThumbnailGenerator(content).thumbnail)
        return super().create(_content=encrypted_content, _thumbnail=encrypted_thumbnail, **kwargs)

    def by_tag(self, tag: str) -> models.QuerySet:
        return self.filter(tag=tag)

    def has_images_with_tag(self, tag: str) -> bool:
        return self.by_tag(tag).exists()

    def classified_by_tag(self) -> List[dict]:
        return [{'tag': tag, 'images': self.by_tag(tag)} for tag in choices.images.TAGS if self.has_images_with_tag(tag)]


class Image(models.Model):
    _content = models.BinaryField()
    _thumbnail = models.BinaryField()
    clinical_session = models.ForeignKey(ClinicalSession, on_delete=models.CASCADE, null=True)
    tag = models.CharField(max_length=20, choices=choices.images.get())

    objects = ImageQuerySet.as_manager()

    def _decrypted_binary_field(self, field):
        return Fernet(settings.IMAGE_ENCRYPTION_KEY).decrypt(field.tobytes())

    @property
    def content(self) -> bytes:
        return self._decrypted_binary_field(self._content)

    @property
    def thumbnail(self) -> bytes:
        return self._decrypted_binary_field(self._thumbnail)

    def can_access(self, user: User) -> bool:
        return self.clinical_session.can_access(user)
