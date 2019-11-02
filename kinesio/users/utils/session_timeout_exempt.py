from functools import wraps


def session_timeout_exempt(view_func):

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.session_timeout_exempt = True
    return wraps(view_func)(wrapped_view)
