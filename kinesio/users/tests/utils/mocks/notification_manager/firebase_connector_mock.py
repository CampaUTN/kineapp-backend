class FirebaseConnectorMock:
    """ Mocks Firebase connection. """
    def __init__(self) -> None:
        self.sent_messages = []

    @property
    def times_called(self) -> int:
        return len(self.sent_messages)

    def notify_single_device(self, registration_id: str, message_title: str, message_body: str) -> None:
        assert type(registration_id) == str, 'Firebase device ID should be a string.'
        assert type(message_title) == str, 'The message title should be a string.'
        assert type(message_body) == str, 'The message body should be a string.'
        self.sent_messages.append({'device_id': registration_id, 'title': message_title, 'body': message_body})

    def reset(self) -> None:
        """ Reset call logs of this mock """
        self.sent_messages = []
