from typing import Callable, Dict, Any
from functools import wraps
from django.conf import settings


def inject_dependencies_on_testing(mocking_configuration: Dict[str, Any]) -> Callable:
    """ This function injects dependencies if we are running django's tests through manage.py.
        The argument should contain keys with the name of named parameters to override
        and the parameter to inject as value.
        For instnace, given:
        @inject_dependencies_on_testing({'x': 100, 'y': 10})
        def function(x, y=0, z=0):
            return x + y + z
        Then function(1000) is going to return 1000 normally but """
    def real_decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            if settings.TESTING:
                # Inject dependencies as kwargs to override original function's default values.
                kwargs.update(mocking_configuration)
            return function(*args, **kwargs)
        return wrapper
    return real_decorator
