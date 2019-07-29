from kinesioapp.utils.test_utils import APITestCase
from rest_framework import status

from ..models import User


class TestPatientsAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423')
        self.another_medic = User.objects.create_user(username='juan55', license='matricula #5343')
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo')
        User.objects.create_user(username='martin', current_medic=self.medic)
        self._log_in(self.medic, '1234')

    def test_get_one_patient(self):
        response = self.client.get(f'/api/v1/patients/{self.patient.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], 'facundo')

    def test_get_all_patients(self):
        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)

    def test_update_one_patient(self):
        data = {'patient': {'current_medic_id': self.another_medic.id}, 'first_name': 'pepe'}
        response = self.client.patch(f'/api/v1/patients/{self.patient.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['current_medic_id'], self.another_medic.id)
