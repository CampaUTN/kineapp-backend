from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


class InvalidTokenException(Exception):
    pass


class GoogleUser:
    def __init__(self, google_token):
        self.account_information = self._validate_and_generate_account_information(google_token)

    def _validate_and_generate_account_information(self, google_token):
        try:

            account_information = id_token.verify_oauth2_token(google_token, requests.Request())

            if account_information['aud'] not in [settings.CLIENT_ID_ANDROID, settings.CLIENT_ID_WEB]:
                raise ValueError('Could not verify audience.')
            elif not self._token_is_valid(account_information):
                raise InvalidTokenException
            else:
                return account_information

        except ValueError:
            raise InvalidTokenException

    @staticmethod
    def _token_is_valid(acc_info):
        return all(key in acc_info for key in ['iss', 'sub', 'given_name', 'family_name', 'email'])

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
