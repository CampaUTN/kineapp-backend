from django.core.validators import validate_comma_separated_integer_list
from django.db import models, transaction
from cryptography.fernet import Fernet
from django.conf import settings
from typing import List, Iterable
import base64
from functools import reduce

from kinesioapp import choices
from users.models import User, Patient
from kinesioapp.utils.thumbnail import ThumbnailGenerator


class VideoQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(owner=user.related_medic)

    def create(self, medic_id: int, **kwargs):
        return super().create(owner=User.objects.get(id=medic_id), **kwargs)


class Video(models.Model):
    name = models.CharField(max_length=255)
    content = models.FileField(upload_to='')
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    objects = VideoQuerySet.as_manager()

    @property
    def url(self) -> str:
        return self.content.url


class ExerciseQuerySet(models.QuerySet):
    def create_multiple(self, days: Iterable[int], **kwargs):
        if not days:
            raise Exception('At least one day should be specified for the exercise')
        elif any(not choices.days.is_valid(day) for day in days):
            raise Exception('At least one days is outside range of valid days [0;6].')
        else:
            with transaction.atomic():
                exercises = [self.create(day=day, **kwargs) for day in days]
        return exercises


class Exercise(models.Model):
    """ If an exercise should be done two times a week, we will create two different exercises:
        one for each of those days. """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=511, default='')
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    day = models.PositiveSmallIntegerField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='exercises')
    done = models.BooleanField(default=False)

    objects = ExerciseQuerySet.as_manager()


class ClinicalSessionQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(patient__user__in=user.related_patients)


class ClinicalSession(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, related_name='sessions', on_delete=models.CASCADE)
    description = models.CharField(default='', max_length=511)

    objects = ClinicalSessionQuerySet.as_manager()

    def can_access(self, user: User) -> bool:
        return self.patient.user in user.related_patients


class ImageQuerySet(models.QuerySet):
    def create(self, content_as_base64: bytes, **kwargs):
        content_as_base64 = content_as_base64.replace(b'\\n', b'').replace(b'\n', b'')  # to fix a bug in the mobile front end.
        encrypted_content = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(content_as_base64)
        encrypted_thumbnail = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(ThumbnailGenerator(content_as_base64).thumbnail)
        return super().create(_content_base64_and_encrypted=encrypted_content,
                              _thumbnail_base64_and_encrypted=encrypted_thumbnail,
                              **kwargs)

    def by_tag(self, tag: str) -> models.QuerySet:
        return self.filter(tag=tag)

    def has_images_with_tag(self, tag: str) -> bool:
        return self.by_tag(tag).exists()

    def classified_by_tag(self) -> List[dict]:
        return [{'tag': tag, 'images': self.by_tag(tag)} for tag in choices.images.TAGS if self.has_images_with_tag(tag)]


class Image(models.Model):
    _content_base64_and_encrypted = models.BinaryField()
    _thumbnail_base64_and_encrypted = models.BinaryField()
    clinical_session = models.ForeignKey(ClinicalSession, on_delete=models.CASCADE, null=True, related_name='images')
    tag = models.CharField(max_length=20, choices=choices.images.get())

    objects = ImageQuerySet.as_manager()

    def _decrypted_binary_field(self, field):
        field = field.tobytes() if type(field) is not bytes else field
        return str(Fernet(settings.IMAGE_ENCRYPTION_KEY).decrypt(field))[2:-1]

    @property
    def content_as_base64(self) -> str:
        return self._decrypted_binary_field(self._content_base64_and_encrypted)

    @property
    def thumbnail_as_base64(self) -> str:
        return self._decrypted_binary_field(self._thumbnail_base64_and_encrypted)

    def can_access(self, user: User) -> bool:
        return self.clinical_session.can_access(user)
