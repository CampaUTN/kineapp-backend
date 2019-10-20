from requests import get as original_get
import time


def get(url: str, *args, expected_status_code: int = 200, **kwargs):
    retries = 0
    response = original_get(url, *args, **kwargs)
    while response.status_code != expected_status_code and retries < 10:
        if retries > 5:
            time.sleep(1)
        response = original_get(url, *args, **kwargs)
    return response
