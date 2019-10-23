from rest_framework import status
from django.utils import timezone

from ..utils.test_utils import APITestCase
from ..models import ClinicalSession
from users.models import User


class TestClinicalSessionSharingtAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now())
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', dni=7357735, birth_date=timezone.now())
        ClinicalSession.objects.create(patient=self.patient.patient)
        ClinicalSession.objects.create(patient=self.patient.patient)
        ClinicalSession.objects.create(patient=self.patient.patient)

    def test_medic_can_access_to_session_if_the_patient_shared_it(self):
        self._log_in(self.medic, '12345')
        self.patient.patient.share_with(self.medic)
        response = self.client.get(f'/api/v1/clinical_sessions_for_patient/{self.patient.id}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 3)

    def test_medic_can_not_access_to_session_if_the_patient_did_not_share_it(self):
        self._log_in(self.medic, '12345')
        response = self.client.get(f'/api/v1/clinical_sessions_for_patient/{self.patient.id}')
        # The status is a 200 but the list is empty!
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 0)
