from django.db import models

from users.models.user import User


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    current_medic = models.ForeignKey(User, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)

    @property
    def related_patients(self) -> models.QuerySet:
        return User.objects.filter(id=self.user.id)

    @property
    def related_medic(self) -> User:
        return self.current_medic
