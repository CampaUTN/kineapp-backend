from PIL import Image
from datetime import datetime
import random
import hashlib
from io import BytesIO
import os
import base64


class ThumbnailGenerator:
    def __init__(self, image_content_as_base64: bytes):
        self._path_base = f'/tmpfs/{self._datetime}_{self._random_int}'
        self._image_content = base64.b64decode(image_content_as_base64)

    @property
    def _datetime(self) -> str:
        return str(datetime.now()).replace(' ', '_').replace(':', '_')

    @property
    def _random_int(self) -> int:
        return random.randint(0, 9999999)

    @property
    def _image_hash(self) -> str:
        return hashlib.md5(self._image_content).hexdigest()

    @property
    def _thumbail_path(self) -> str:
        return f'{self._path_base}_{self._image_hash}_thumbnail.jpg'

    @property
    def thumbnail(self) -> bytes:
        try:
            im = Image.open(BytesIO(self._image_content))
            size = 320, 320
            im.thumbnail(size)
            im.save(self._thumbail_path)
            with open(self._thumbail_path, 'rb') as thumbnail_file:
                thumbnail_content = thumbnail_file.read()
            return base64.b64encode(thumbnail_content)
        finally:
            # To assure that the file will be deleted regardless any exception
            os.remove(self._thumbail_path)
