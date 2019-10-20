from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from django.conf import settings
import textwrap
import base64

from . import retry_requests as requests


class InformationNotAccessibleFromTokenException(Exception):
    pass


class GoogleRejectsTokenException(Exception):
    pass


class InvalidAudienceException(Exception):
    pass


class GoogleUser:
    def __init__(self, google_token: str) -> None:
        self.account_information = self._validate_and_generate_account_information(google_token)

    def _validate_and_generate_account_information(self, google_token: str) -> dict:
        account_information = self._get_account_information(google_token)
        if account_information['aud'] not in [settings.CLIENT_ID_ANDROID, settings.CLIENT_ID_WEB]:
            raise InvalidAudienceException('Audience is neither the client_id of the web or the mobile application.')
        if not self._account_information_is_valid(account_information):
            raise InformationNotAccessibleFromTokenException(textwrap.dedent(""" Some information is not accesible with the given token.
                                                                                 The back end needs access to the following fields:
                                                                                 aud, iss, sub, given_name, family_name, email, picture. """))
        return account_information

    @staticmethod
    def _account_information_is_valid(acc_info: dict) -> bool:
        return all(key in acc_info for key in ['aud', 'iss', 'sub', 'given_name', 'family_name', 'email', 'picture'])

    @staticmethod
    def _get_account_information(google_token) -> dict:
        try:
            account_information = id_token.verify_oauth2_token(google_token, google_auth_requests.Request())
        except ValueError:
            raise GoogleRejectsTokenException('Google rejects the token.')
        return account_information

    @property
    def username_is_valid(self) -> bool:
        return self.account_information['iss'].lower().split('://').pop().strip() == 'accounts.google.com'

    @property
    def picture_base64(self) -> bytes:
        picture_url = self.account_information['picture']
        picture = requests.get(picture_url).content
        return base64.b64encode(picture)

    @property
    def user_id(self) -> str:
        return self.account_information['sub']

    @property
    def first_name(self) -> str:
        return self.account_information['given_name']

    @property
    def last_name(self) -> str:
        return self.account_information['family_name']

    @property
    def email(self) -> str:
        return self.account_information['email']
