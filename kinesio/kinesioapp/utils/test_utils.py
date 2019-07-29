from rest_framework.test import APITestCase as DRFAPITestCase

from users.models import User


class APITestCase(DRFAPITestCase):
    def _log_in(self, user: User, password: str) -> None:
        logged_in = self.client.login(username=user.username, password=password)
        self.assertTrue(logged_in)
