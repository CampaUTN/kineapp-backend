from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings


def binary_field_to_string(field: models.BinaryField, decrypt: bool = False) -> str:
    field = field.tobytes() if type(field) is not bytes else field
    if decrypt:
        field = Fernet(settings.IMAGE_ENCRYPTION_KEY).decrypt(field)
    return str(field)[2:-1]  # The slices remove "b'" at the start and a single quote at the end
