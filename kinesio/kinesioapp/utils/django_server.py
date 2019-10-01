from django.conf import settings


class DjangoServerConfiguration:
    @property
    def ip(self):
        return settings.PUBLIC_IP

    @property
    def port(self):
        return settings.DEFAULT_PORT

    @property
    def base_url(self):
        return f'{self.ip}:{self.port}'
