import sys
import logging

# Import default settings
from . settings import *

# Import secrets.py from current directory.
# Sensitive information, such as API keys, should be placed on a secrets.py file and not pushed to the repository.
try:
    from .settings_production import (FIREBASE_API_KEY, IMAGE_ENCRYPTION_KEY, SECRET_KEY)
except ModuleNotFoundError:
    logging.warning('Secrets file not found!')

# Override some settings if running tests
if sys.argv[1] == 'test':  # We are running tests
    from .settings_testing import (TESTING, FFMPEG_GLOBAL_OPTIONS)
