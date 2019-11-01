from users.utils.notification_manager import NotificationManager
from .firebase_connector_mock import FirebaseConnectorMock


class NotificationManagerMock(NotificationManager):
    def __init__(self) -> None:
        super().__init__()
        self.firebase_connector = FirebaseConnectorMock()

    def reset(self) -> None:
        """ Reset call logs of this mock """
        self.firebase_connector.reset()
