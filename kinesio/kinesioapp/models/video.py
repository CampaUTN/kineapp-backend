from django.db import models

from kinesioapp.utils.django_server import DjangoServerConfiguration
from users.models import User


class VideoQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(owner=user.related_medic)

    def create(self, medic_id: int, **kwargs) -> models.Model:
        return super().create(owner=User.objects.get(id=medic_id), **kwargs)


class Video(models.Model):
    name = models.CharField(max_length=255)
    content = models.FileField(upload_to='')
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    objects = VideoQuerySet.as_manager()

    @property
    def url(self) -> str:
        return f'http://{DjangoServerConfiguration().base_url}{self.content.url}'

    def can_edit_and_delete(self, user: User) -> bool:
        return self.owner == user

    def can_view(self, user: User) -> bool:
        return self.owner == user.related_medic
