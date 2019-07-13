from google.oauth2 import id_token
from google.auth.transport import requests


class InvalidTokenException(Exception):
    pass


class GoogleConnector:
    def __init__(self, google_token):
        self.google_token = self._validate_and_set_account_information(google_token)

    def _validate_and_set_account_information(self, google_token):
        try:
            self.account_information = id_token.verify_oauth2_token(google_token,
                                                                    requests.Request(),
                                                                    '1093191472549-9gk2os2g3hm2qa1bhrhr1ab0cl7r5qkb.apps.googleusercontent.com')
        except ValueError:
            raise InvalidTokenException
        else:
            if not self._token_is_valid():
                raise InvalidTokenException

    @property
    def _token_is_valid(self):
        return 'iss' in self.account_information and 'sub' in self.account_information

    @property
    def username_is_valid(self):
        return self.account_information['iss'] in ['accounts.google.com', 'https://accounts.google.com']

    @property
    def user_id(self):
        return self.account_information['sub']
