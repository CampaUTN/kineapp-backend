from __future__ import annotations
from django.db import models
from django.db.models import Q

from users.models import User, Patient, Medic
from kinesioapp.utils.models_mixins import CanViewModelMixin


class ClinicalSessionQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> ClinicalSessionQuerySet:
        # The first Q object gives access to the patient itself and its medic.
        # The second one gives access to medics to whom the patient shared its clinical history.
        return self.filter(Q(patient__user__in=user.related_patients) | Q(patient__in=user.shared.all()))


class ClinicalSession(models.Model, CanViewModelMixin):
    class Meta:
        ordering = ['-id']
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, related_name='sessions', on_delete=models.CASCADE)
    description = models.CharField(default='', max_length=511)
    created_by = models.ForeignKey(Medic, related_name='creator', blank=True, null=True, on_delete=models.SET_NULL)

    objects = ClinicalSessionQuerySet.as_manager()

    def can_edit_and_delete(self, user: User) -> bool:
        return self.patient.user in user.related_patients

    def can_view(self, user: User) -> bool:
        return self.can_edit_and_delete(user) or user in self.patient.shared_history_with.all()
