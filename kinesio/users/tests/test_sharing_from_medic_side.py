from kinesioapp.utils.test_utils import APITestCase
from datetime import datetime
from rest_framework import status

from ..models import User


class TestSharingFromMedicSide(APITestCase):
    def setUp(self) -> None:
        """ Test sharing on '/api/v1/patients' endpoint.
            That endpoint is for patients to get data of patients who allowed them. """
        self.current_medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                                      dni=39203040, birth_date=datetime.now(),
                                                      first_name='maria', last_name='alvarez')
        self.medic = User.objects.create_user(username='juan55', password='1234', license='matricula #5343',
                                                    dni=42203088, birth_date=datetime.now(),
                                                    first_name='juan', last_name='gomez')
        self.patient = User.objects.create_user(username='martin', current_medic=self.current_medic,
                                                dni=15505050, birth_date=datetime.now())
        self.another_patient = User.objects.create_user(username='sofia', current_medic=self.current_medic,
                                                        dni=65345435, birth_date=datetime.now())

    def test_share_no_patients(self):
        self._log_in(self.medic, '1234')
        response = self.client.get('/api/v1/patients')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json()['non_assigned_patients'], [])

    def test_share_of_one_patient(self):
        self._log_in(self.medic, '1234')
        self.patient.patient.share_with(self.medic)
        response = self.client.get('/api/v1/patients')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['non_assigned_patients'][0]['first_name'], self.patient.first_name)

    def test_share_of_two_patients(self):
        self._log_in(self.medic, '1234')
        self.patient.patient.share_with(self.medic)
        self.another_patient.patient.share_with(self.medic)
        response = self.client.get('/api/v1/patients')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['non_assigned_patients']), 2)

    def test_current_medic_not_affected_by_sharing(self):
        self._log_in(self.current_medic, '1234')
        self.patient.patient.share_with(self.medic)
        response = self.client.get('/api/v1/patients')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patients'][0]['patient']['current_medic']['id'], self.current_medic.id)
