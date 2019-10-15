from django.conf import settings


class DjangoServerConfiguration:
    @property
    def ip(self) -> str:
        return settings.PUBLIC_IP

    @property
    def port(self) -> str:
        return settings.DEFAULT_PORT

    @property
    def base_url(self) -> str:
        return f'{self.ip}:{self.port}'
