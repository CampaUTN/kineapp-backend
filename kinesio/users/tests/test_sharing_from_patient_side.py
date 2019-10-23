from datetime import datetime

from rest_framework import status

from kinesioapp.utils.test_utils import APITestCase
from ..models import User


class TestSharingFromPatientSide(APITestCase):
    def setUp(self) -> None:
        self.current_medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                                      dni=39203040, birth_date=datetime.now(),
                                                      first_name='maria', last_name='alvarez')
        self.first_medic = User.objects.create_user(username='juan55', license='matricula #5343',
                                                    dni=42203088, birth_date=datetime.now(),
                                                    first_name='juan', last_name='gomez')
        self.second_medic = User.objects.create_user(username='facundo', license='matricula #1111',
                                                     dni=5643535, birth_date=datetime.now(),
                                                     first_name='facundo', last_name='ramirez')
        self.patient = User.objects.create_user(username='martin', password='1234', current_medic=self.current_medic,
                                                dni=15505050, birth_date=datetime.now())

    def test_share_with_no_medics(self):
        self._log_in(self.patient, '1234')
        response = self.client.get('/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json()['patient']['shared_history_with'], [])

    def test_share_with_one_medic(self):
        self._log_in(self.patient, '1234')
        self.patient.patient.share_with(self.first_medic)
        response = self.client.get('/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['shared_history_with'][0]['first_name'], self.first_medic.first_name)

    def test_share_with_one_medic_through_api(self):
        self._log_in(self.patient, '1234')
        data = {'user_to_share_with': self.first_medic.id}
        response = self.client.post(f'/api/v1/share_sessions/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['shared_history_with'][0]['first_name'], self.first_medic.first_name)

    def test_try_share_with_invalid_user_through_api(self):
        self._log_in(self.patient, '1234')
        data = {'user_to_share_with': 12345}
        response = self.client.post(f'/api/v1/share_sessions/', data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_with_two_medics(self):
        self._log_in(self.patient, '1234')
        self.patient.patient.share_with(self.first_medic)
        self.patient.patient.share_with(self.second_medic)
        response = self.client.get('/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['patient']['shared_history_with']), 2)

    def test_current_medic_not_affected_by_sharing(self):
        self._log_in(self.patient, '1234')
        self.patient.patient.share_with(self.first_medic)
        self.patient.patient.share_with(self.second_medic)
        response = self.client.get('/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['current_medic']['id'], self.current_medic.id)

    def test_cancel_sharing_with_medic(self):
        self._log_in(self.patient, '1234')
        self.patient.patient.share_with(self.first_medic)
        self.patient.patient.share_with(self.second_medic)
        self.patient.patient.unshare_with(self.first_medic)
        response = self.client.get('/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['patient']['shared_history_with']), 1)
        self.assertEqual(response.json()['patient']['shared_history_with'][0]['last_name'], self.second_medic.last_name)

    def test_cancel_share_with_medic_through_api(self):
        self._log_in(self.patient, '1234')
        data = {'user_to_share_with': self.first_medic.id}
        response = self.client.post(f'/api/v1/share_sessions/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['shared_history_with'][0]['first_name'], self.first_medic.first_name)
        data = {'user_to_unshare_with': self.first_medic.id}
        response = self.client.post(f'/api/v1/unshare_sessions/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['patient']['shared_history_with']), 0)
