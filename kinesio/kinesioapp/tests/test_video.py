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
        self.file_name = 'kinesio.jpg'
        self.media_path = f'/kinesio/kinesio/media/{self.file_name}'

    def tearDown(self) -> None:
        os.remove(self.media_path)

    def get_file_descriptor(self):
        # It's a image, but to test resource serving it's the same.
        return open(f'/kinesio/kinesio/kinesioapp/tests/resources/{self.file_name}', 'rb')

    def test_get_video(self):
        self._log_in(self.medic, '12345')
        file = SimpleUploadedFile(self.file_name, self.get_file_descriptor().read())
        video = Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        response = requests.get(f'http://localhost{video.url}')  # We request the image from the outside because otherwise is unreachable.
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.content, self.get_file_descriptor().read())

    def test_upload_video(self):
        self._log_in(self.medic, '12345')
        data = {'content': self.get_file_descriptor(), 'name': 'leg exercise'}
        response = self.client.post('/api/v1/video/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.json()['url'], '/media/kinesio.jpg')

    def test_uploaded_video_owner_is_the_uploader(self):
        self._log_in(self.medic, '12345')
        data = {'content': self.get_file_descriptor(), 'name': 'leg exercise'}
        response = self.client.post('/api/v1/video/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Video.objects.all()[0].owner, self.medic)

    def test_delete_video(self):
        self._log_in(self.medic, '12345')
        file = SimpleUploadedFile(self.file_name, self.get_file_descriptor().read())
        video = Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        response = self.client.delete(f'/api/v1/video/{video.id}')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Video.objects.count(), 0)

    def test_fail_to_delete_a_video_of_another_medic(self):
        another_medic = User.objects.create_user(username='raul22', password='12345', first_name='raul',
                                                 last_name='sanchez', license='matricula #5555',
                                                 dni=9203040, birth_date=timezone.now())
        self._log_in(another_medic, '12345')
        file = SimpleUploadedFile(self.file_name, self.get_file_descriptor().read())
        video = Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        response = self.client.delete(f'/api/v1/video/{video.id}')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(Video.objects.count(), 1)
