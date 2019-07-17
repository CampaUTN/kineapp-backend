from .testing_detection import is_testing_mode
from .mocks import GoogleUser


def mock_google_user(original_function):
    def new_function(request):
        return original_function(request, google_user_class=GoogleUser) if is_testing_mode() else original_function(request)
    return new_function
