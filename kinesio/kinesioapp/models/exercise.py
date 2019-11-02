from __future__ import annotations
from django.db import models, transaction
from typing import List, Iterable
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import datetime

from kinesioapp import choices
from users.models import User, Patient
from kinesioapp.utils.models_mixins import CanViewModelMixin
from .video import Video
from users.utils.notification_manager import NotificationManager
from users.tests.utils.mock_decorators import inject_dependencies_on_testing
from users.tests.utils.mocks import NotificationManagerMock


class ExerciseQuerySet(models.QuerySet):
    def create_multiple(self, days: Iterable[int], **kwargs: dict) -> List[Exercise]:
        if not days:
            raise Exception('At least one day should be specified for the exercise')
        elif any(not choices.days.is_valid(day) for day in days):
            raise Exception('At least one days is outside range of valid days [0;6].')
        else:
            with transaction.atomic():
                exercises = [self.create(day=day, **kwargs) for day in days]
        return exercises

    def reset_status(self):
        result = self.update(done=False)
        for item in self:
            item.save()
        return result


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

    def reset_status(self):
        self.done = False
        self.save()

    @inject_dependencies_on_testing({'notification_manager': NotificationManagerMock()})
    def send_reminder_if_necessary(self, notification_manager: NotificationManager = NotificationManager()):
        if datetime.date.today().weekday() == self.day:
            notification_manager.send_exercise_reminder(self)

# Signals
@receiver(post_save, sender=Exercise)
@inject_dependencies_on_testing({'notification_manager': NotificationManagerMock()})
def report_exercise_saved(sender: type,
                          instance: Exercise,
                          created: bool,
                          notification_manager: NotificationManager = NotificationManager(),
                          **kwargs: dict) -> None:
    notification_manager.routine_changed(instance.patient.user)


@receiver(post_delete, sender=Exercise)
@inject_dependencies_on_testing({'notification_manager': NotificationManagerMock()})
def report_exercise_deleted(sender: type,
                            instance: Exercise,
                            notification_manager: NotificationManager = NotificationManager(),
                            **kwargs: dict) -> None:
    notification_manager.routine_changed(instance.patient.user)
