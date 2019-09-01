from rest_framework import status
from django.utils import timezone
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
import requests
import os

from ..utils.test_utils import APITestCase
from ..models import Video
from users.models import User
from .. import choices


class TestVideoAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic,
                                                dni=564353, birth_date=timezone.now())
        with self.get_file_descriptor() as file:
            self.content = file.read()
        self._log_in(self.medic, '12345')
        self.file_name = 'test_file_name.remove_me'
        self.file_path = f'/kinesio/kinesio/media/{self.file_name}'

    def tearDown(self) -> None:
        os.remove(self.file_path)

    def get_file_descriptor(self):
        # It's a image, but to test resource serving it's the same.
        return open('/kinesio/kinesio/kinesioapp/tests/resources/kinesio.jpg', 'rb')

    def test_get_video(self):
        file = SimpleUploadedFile(self.file_name, b'content')
        video = Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        response = requests.get(f'http://localhost{video.url}')  # We request the image from the outside because otherwise is unreachable.
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.content, b'content')
