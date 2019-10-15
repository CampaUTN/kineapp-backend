from django.http.request import HttpRequest
from django.http.response import HttpResponse
from typing import Callable

from .testing_detection import is_testing_mode
from .mocks import GoogleUser


def mock_google_user_on_tests(original_function: Callable) -> Callable:
    def new_function(request: HttpRequest) -> HttpResponse:
        return original_function(request, google_user_class=GoogleUser) if is_testing_mode() else original_function(request)
    return new_function
