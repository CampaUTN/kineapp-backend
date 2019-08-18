from rest_framework import status

from ..utils.test_utils import APITestCase
from .. import models
from ..models import ClinicalSession, Image
from ..utils.thumbnail import ThumbnailGenerator
from users.models import User


class TestImageAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        self.clinical_session = ClinicalSession.objects.create(status=models.PENDING,
                                                               patient=self.patient.patient)
        with self.get_file_descriptor() as file:
            self.content = file.read()
            self.thumbnail = ThumbnailGenerator(self.content).thumbnail
        self._log_in(self.medic, '12345')

    def get_file_descriptor(self):
        return open('/kinesio/kinesio/kinesioapp/tests/resources/kinesio.jpg', 'rb')

    def test_thumbnail_is_smaller(self):
        self.assertTrue(len(self.thumbnail) < len(self.content))

    def test_image_data_on_database_is_encrypted(self):
        image = Image.objects.create(content=self.content, clinical_session=self.clinical_session)
        self.assertNotEquals(image._content, self.content)

    def test_thumbnail_data_on_database_is_encrypted(self):
        image = Image.objects.create(content=self.content, clinical_session=self.clinical_session)
        self.assertNotEquals(image._thumbnail, self.thumbnail)

    def test_create_image(self):
        data = {'content': self.get_file_descriptor(), 'clinical_session_id': self.clinical_session.pk}
        response = self.client.post('/api/v1/image/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.get().content, self.content)

    def test_delete_image(self):
        image = Image.objects.create(content=self.content, clinical_session=self.clinical_session)
        response = self.client.delete(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Image.objects.count(), 0)

    def test_get_image(self):
        image = Image.objects.create(content=self.content, clinical_session=self.clinical_session)
        response = self.client.get(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(type(response.content), bytes)
        self.assertEquals(response.content, self.content)

    def test_get_thumbnail(self):
        image = Image.objects.create(content=self.content, clinical_session=self.clinical_session)
        response = self.client.get(f'/api/v1/image/{image.id}?thumbnail=true')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(type(response.content), bytes)
        self.assertEquals(response.content, self.thumbnail)
