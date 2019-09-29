from django.db import models, transaction
from typing import List, Iterable

from kinesioapp import choices
from users.models import User, Patient
from kinesioapp.utils.models_mixins import CanViewModelMixin
from .video import Video


class ExerciseQuerySet(models.QuerySet):
    def create_multiple(self, days: Iterable[int], **kwargs) -> List[models.Model]:
        if not days:
            raise Exception('At least one day should be specified for the exercise')
        elif any(not choices.days.is_valid(day) for day in days):
            raise Exception('At least one days is outside range of valid days [0;6].')
        else:
            with transaction.atomic():
                exercises = [self.create(day=day, **kwargs) for day in days]
        return exercises


class Exercise(models.Model, CanViewModelMixin):
    """ If an exercise should be done two times a week, we will create two different exercises:
        one for each of those days. """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=511, default='')
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    day = models.PositiveSmallIntegerField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='exercises')
    done = models.BooleanField(default=False)

    objects = ExerciseQuerySet.as_manager()

    def can_edit_and_delete(self, user: User) -> bool:
        return self.patient.user in user.related_patients
