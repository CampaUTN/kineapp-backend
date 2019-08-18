from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings

from users.models import User, Patient
from kinesioapp.utils.thumbnail import ThumbnailGenerator


PENDING = 'pending'
FINISHED = 'finished'
CANCELLED = 'cancelled'


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


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    homework_exercise = models.ForeignKey(HomeworkExercise, on_delete=models.CASCADE, null=True)


class Video(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True)


class ClinicalSessionQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(patient__user__in=user.related_patients)


class ClinicalSession(models.Model):
    SESSION_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('F', 'FINISHED'),
        ('C', 'CANCELLED')
    ]
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=SESSION_STATUS_CHOICES, default='PENDING')
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


class Image(models.Model):
    _content = models.BinaryField()
    _thumbnail = models.BinaryField()
    clinical_session = models.ForeignKey(ClinicalSession, on_delete=models.CASCADE, null=True)

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
