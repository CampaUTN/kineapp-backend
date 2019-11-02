from users.utils.notification_manager import NotificationManager
from .firebase_connector_mock import FirebaseConnectorMock
from users.models import User


class NotificationManagerMock(NotificationManager):
    def __init__(self) -> None:
        super().__init__()
        self.firebase_connector = FirebaseConnectorMock()
        self.times_called = 0

    def _send_notification(self, user: User, title: str, body: str) -> None:
        self.times_called += 1
        return super()._send_notification(user, title, body)

    def reset(self) -> None:
        """ Reset call logs of this mock """
        self.firebase_connector.reset()
        self.times_called = 0
