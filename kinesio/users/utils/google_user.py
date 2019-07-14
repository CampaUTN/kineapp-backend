from google.oauth2 import id_token
from google.auth.transport import requests


class InvalidTokenException(Exception):
    pass


class GoogleUser:
    def __init__(self, google_token):
        self.google_token = self._validate_and_set_account_information(google_token)

    def _validate_and_set_account_information(self, google_token):
        try:
            self.account_information = id_token.verify_oauth2_token(google_token,
                                                                    requests.Request(),
                                                                    '407408718192.apps.googleusercontent.com')
        except ValueError:
            raise InvalidTokenException
        else:
            if not self._token_is_valid:
                raise InvalidTokenException

    @property
    def _token_is_valid(self):
        return all(key in self.account_information for key in ['iss', 'sub', 'given_name', 'family_name', 'email'])

    @property
    def username_is_valid(self):
        return self.account_information['iss'] in ['accounts.google.com', 'https://accounts.google.com']

    @property
    def user_id(self):
        return self.account_information['sub']

    @property
    def first_name(self):
        return self.account_information['given_name']

    @property
    def last_name(self):
        return self.account_information['family_name']

    @property
    def email(self):
        return self.account_information['email']
