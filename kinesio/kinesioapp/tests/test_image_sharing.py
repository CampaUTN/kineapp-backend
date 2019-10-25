from rest_framework import status
from django.utils import timezone
import base64

from ..utils.test_utils import APITestCase
from ..models import ClinicalSession, Image
from ..utils.thumbnail import ThumbnailGenerator
from users.models import User
from .. import choices


class TestImageSharingAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', dni=564353, birth_date=timezone.now())
        self.clinical_session = ClinicalSession.objects.create(patient=self.patient.patient)
        with self.get_file_descriptor() as file:
            self.content = base64.b64encode(file.read())
        self._log_in(self.medic, '12345')
        self.image = Image.objects.create(content_as_base64=self.content, clinical_session=self.clinical_session,
                                          tag=choices.images.FRONT)

    def get_file_descriptor(self):
        return open('/kinesio/kinesio/kinesioapp/tests/resources/kinesio.jpg', 'rb')

    def test_medic_can_access_to_image_if_the_patient_shared_its_session(self):
        self._log_in(self.medic, '12345')
        self.patient.patient.share_with(self.medic)
        response = self.client.get(f'/api/v1/image/{self.image.id}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()['id'], self.image.id)

    def test_medic_can_not_access_to_image_if_the_patient_did_not_share_its_session(self):
        self._log_in(self.medic, '12345')
        response = self.client.get(f'/api/v1/image/{self.image.id}')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
