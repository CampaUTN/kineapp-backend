from django.db import models

from users.models import User, Patient
from kinesioapp.utils.models_mixins import CanViewModelMixin


class ClinicalSessionQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(patient__user__in=user.related_patients)


class ClinicalSession(models.Model, CanViewModelMixin):
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, related_name='sessions', on_delete=models.CASCADE)
    description = models.CharField(default='', max_length=511)

    objects = ClinicalSessionQuerySet.as_manager()

    def can_edit_and_delete(self, user: User) -> bool:
        return self.patient.user in user.related_patients
