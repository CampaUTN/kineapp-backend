from django.db import models

from users.models.user import User, UserQuerySet


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    current_medic = models.ForeignKey(User, related_name='patients', on_delete=models.SET_NULL,
                                      default=None, blank=True, null=True)
    shared_history_with = models.ManyToManyField(User, related_name='shared')

    @property
    def related_patients(self) -> UserQuerySet:
        return User.objects.filter(id=self.user.id)

    @property
    def related_medic(self) -> User:
        return self.current_medic

    def share_with(self, user: User) -> None:
        self.shared_history_with.add(user)

    def unshare_with(self, user: User) -> None:
        self.shared_history_with.remove(user)
