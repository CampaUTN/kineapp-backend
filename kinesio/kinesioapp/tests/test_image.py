from rest_framework import status
from django.utils import timezone
import base64

from ..utils.test_utils import APITestCase
from ..models import ClinicalSession, Image
from ..utils.thumbnail import ThumbnailGenerator
from users.models import User
from .. import choices


class TestImageAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic,
                                                dni=564353, birth_date=timezone.now())
        self.clinical_session = ClinicalSession.objects.create(patient=self.patient.patient)
        with self.get_file_descriptor() as file:
            self.content = base64.b64encode(file.read())
            self.thumbnail = ThumbnailGenerator(self.content).thumbnail
        self._log_in(self.medic, '12345')

    def get_file_descriptor(self):
        return open('/kinesio/kinesio/kinesioapp/tests/resources/kinesio.jpg', 'rb')

    def test_thumbnail_is_smaller(self):
        self.assertTrue(len(self.thumbnail) < len(self.content))

    def test_image_data_on_database_is_encrypted(self):
        image = Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session, tag=choices.images.FRONT)
        self.assertNotEquals(image._content_base64_and_encrypted, self.content)

    def test_thumbnail_data_on_database_is_encrypted(self):
        image = Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session, tag=choices.images.FRONT)
        self.assertNotEquals(image._thumbnail_base64_and_encrypted, self.thumbnail)

    def test_create_image(self):
        data = {'content': self.content, 'clinical_session_id': self.clinical_session.pk, 'tag': 'F'}
        response = self.client.post('/api/v1/image/', data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(bytes(Image.objects.get().content_as_base64.encode('utf-8')), self.content)

    def test_delete_image(self):
        image = Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session, tag=choices.images.FRONT)
        response = self.client.delete(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(Image.objects.count(), 0)

    def test_get_image(self):
        image = Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session, tag=choices.images.FRONT)
        response = self.client.get(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(type(response.json()['content']), str)
        self.assertEquals(bytes(response.json()['content'].encode('utf-8')), self.content)

    def test_images_by_tag(self):
        Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session,
                             tag=choices.images.FRONT)
        Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session,
                             tag=choices.images.BACK)
        Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session,
                             tag=choices.images.BACK)
        Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session,
                             tag=choices.images.RIGHT)
        self.assertEquals(len(Image.objects.classified_by_tag()), 3)
        self.assertEquals(sum([item['images'].count() for item in Image.objects.classified_by_tag()]), 4)
