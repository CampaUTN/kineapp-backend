from rest_framework import status
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import requests
import os
from django.conf import settings

from ..utils.test_utils import APITestCase
from ..models import Video
from users.models import User


class TestVideoAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic,
                                                dni=564353, birth_date=timezone.now())
        self.file_name = 'test_video.mp4'
        self.media_path = f'/kinesio/deployment/media/'

    def tearDown(self) -> None:
        os.remove(f'{self.media_path}{self.file_name}')
        os.remove(f'{self.media_path}{self.file_name}_thumb.jpg')

    def get_media_files(self):
        return [f'{self.media_path}{file}' for file in os.listdir(self.media_path)]

    def get_file_descriptor(self):
        return open(f'/kinesio/kinesio/kinesioapp/tests/resources/{self.file_name}', 'rb')

    def test_get_video(self):
        self._log_in(self.medic, '12345')
        file = SimpleUploadedFile(self.file_name, self.get_file_descriptor().read())
        video = Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        # We request the video from the outside because otherwise is unreachable.
        response = requests.get(video.url.replace(f'{settings.PUBLIC_IP}:80', 'localhost'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.content, self.get_file_descriptor().read())

    def test_thumbnail_file_is_generated_after_video_creation(self):
        self._log_in(self.medic, '12345')
        file = SimpleUploadedFile(self.file_name, self.get_file_descriptor().read())
        # Ensure that there are no files from previous tests that may induce to mislead results
        self.assertEquals(len(self.get_media_files()), 0)
        Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        # There should be two files: the video itself and the thumb
        self.assertEquals(len(self.get_media_files()), 2)

    def test_thumbnail_url_is_generated_after_video_creation(self):
        self._log_in(self.medic, '12345')
        file = SimpleUploadedFile(self.file_name, self.get_file_descriptor().read())
        # Ensure that there are no files from previous tests that may induce to mislead results
        self.assertEquals(len(self.get_media_files()), 0)
        video = Video.objects.create(name='leg exercise', content=file, medic_id=self.medic.id)
        # There should be two files: the video itself and the thumb
        self.assertEquals(video.thumbnail_url.replace(settings.PUBLIC_IP, '127.0.0.1'), 'http://127.0.0.1:80/media/test_video.mp4_thumb.jpg')

    def test_upload_video(self):
        self._log_in(self.medic, '12345')
        data = {'content': self.get_file_descriptor(), 'name': 'leg exercise'}
        response = self.client.post('/api/v1/video/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        # Do not check the IP because it may change
        self.assertEquals(response.json()['url'].replace(settings.PUBLIC_IP, '127.0.0.1'), 'http://127.0.0.1:80/media/test_video.mp4')

    def test_uploaded_video_owner_is_the_uploader(self):
        self._log_in(self.medic, '12345')
        data = {'content': self.get_file_descriptor(), 'name': 'leg exercise'}
        response = self.client.post('/api/v1/video/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Video.objects.all()[0].owner, self.medic.medic)

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
