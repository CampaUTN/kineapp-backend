import functools


def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(function):
        @functools.wraps(function)
        def inner_wrapper(*args, **kwargs):
            with lock:
                return function(*args, **kwargs)
        return inner_wrapper
    return wrapper
