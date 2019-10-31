# Send to single device.
from pyfcm import FCMNotification
from django.conf import settings


class NotificationManager:
    def __init__(self) -> None:
        self.push_service = FCMNotification(api_key=settings.FIREBASE_API_KEY)

    def send_notification(self, device_registration_id: str, title: str, body: str) -> None:
        self.push_service.notify_single_device(registration_id=device_registration_id,
                                               message_title=title,
                                               message_body=body)
