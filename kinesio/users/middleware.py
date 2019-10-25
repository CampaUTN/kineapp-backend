import time
from typing import Optional
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from rest_framework.status import HTTP_401_UNAUTHORIZED
from kinesio.settings import SESSION_TIMEOUT_KEY

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_view(self, request, callback, callback_args, callback_kwargs) -> Optional[HttpResponse]:
        if not hasattr(request, "session") or request.session.is_empty():
            return

        if getattr(callback, 'session_timeout_exempt', False):
            return

        init_time = request.session.setdefault(SESSION_TIMEOUT_KEY, time.time())

        expire_seconds = getattr(
            settings, "SESSION_EXPIRE_SECONDS", settings.SESSION_COOKIE_AGE
        )

        session_is_expired = time.time() - init_time > expire_seconds

        if session_is_expired:
            request.session.flush()
            return HttpResponse('Unauthorized', status=HTTP_401_UNAUTHORIZED)


        expire_since_last_activity = getattr(
            settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY", False
        )
        grace_period = getattr(
            settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD", 1
        )

        if expire_since_last_activity and time.time() - init_time > grace_period:
            request.session[SESSION_TIMEOUT_KEY] = time.time()