from kinesioapp.utils.test_utils import APITestCase
from rest_framework import status
from django.utils import timezone

from ..models import User


class ChangeDeviceIDAPI(APITestCase):
    def setUp(self) -> None:
        self.medic_user = User.objects.create_user(username='juan22', password='1234', license='matricula #4942',
                                                   dni=39203040, birth_date=timezone.now())
        self.patient_user = User.objects.create_user(username='maria', password='1234',
                                                     dni=533523, birth_date=timezone.now())

    def test_device_id_changed_for_medic_user(self):
        self._log_in(self.medic_user, '1234')
        response = self.client.post('/api/v1/login/', {'firebase_device_id': 'AAAA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.medic_user.firebase_device_id, 'AAAA')

    def test_device_id_changed_for_patient_user(self):
        self._log_in(self.patient_user, '1234')
        response = self.client.post('/api/v1/login/', {'firebase_device_id': 'BBBB'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.patient_user.firebase_device_id, 'BBBB')

    def test_device_id_change_endpoint_fails_without_device_id(self):
        self._log_in(self.patient_user, '1234')
        response = self.client.post('/api/v1/login/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
