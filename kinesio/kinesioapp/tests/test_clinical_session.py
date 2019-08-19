from rest_framework import status
from datetime import datetime
from django.utils import timezone

from ..utils.test_utils import APITestCase
from ..models import ClinicalSession
from users.models import User


class TestClinicalSessionOnPatientAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic,
                                                dni=7357735, birth_date=timezone.now())
        User.objects.create_user(first_name='maria', last_name='gomez', username='mgomez',
                                 dni=2432457, birth_date=timezone.now())
        ClinicalSession.objects.create(patient=self.patient.patient)
        ClinicalSession.objects.create(patient=self.patient.patient)
        ClinicalSession.objects.create(patient=self.patient.patient)

    def test_get_clinical_sessions_for_a_patient(self):
        self._log_in(self.patient, '12345')
        response = self.client.get(f'/api/v1/patients/details/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['patient']['sessions']), 3)

    def test_get_clinical_sessions_for_patients_of_the_medic(self):
        self._log_in(self.medic, '12345')
        response = self.client.get(f'/api/v1/patients/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data'][0]['patient']['sessions']), 3)


class TestClinicalSessionCreateAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic,
                                                dni=3342342, birth_date=timezone.now())
        self._log_in(self.medic, '12345')

    def test_create_clinical_session(self):
        data = {'date': datetime.now(), 'status': 'P', 'patient_id': self.patient.id}
        response = self.client.post('/api/v1/clinical_sessions/', data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalSession.objects.count(), 1)
