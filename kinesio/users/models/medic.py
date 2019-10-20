from __future__ import annotations
from django.db import models

from users.models.user import User, UserQuerySet


class MedicManager(models.Manager):
    def _fixed_license(self, license: str) -> str:
        if license is not None:
            license = license.strip() if license.strip() != '' else None
        return license

    def create(self, user: User, license: str, **kwargs: dict) -> Medic:
        return super().create(user=user, license=self._fixed_license(license), **kwargs)


class Medic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license = models.CharField(max_length=100, db_index=True, unique=True)

    objects = MedicManager()

    @property
    def related_patients(self) -> UserQuerySet:
        return User.objects.filter(id__in=self.user.patients.values('id'))

    @property
    def related_medic(self) -> User:
        return self.user
