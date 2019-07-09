import subprocess
from django.test import TestCase
from rest_framework import status
from datetime import datetime
from rest_framework.test import APITestCase

from . import models
from .models import ClinicalHistory, ClinicalSession
from users.models import CustomUser


class TestPEP8(TestCase):
    def test_pep8(self):
        output = subprocess.check_output(
            ["find", "/kinesio/kinesio/",
             "-type", "f",
             "-name", "*.py",
             "-exec", "pycodestyle",
             "--max-line-length=34000",
             "--ignore=E121,E123,E126,E226,E24,E704,W503,E741,E722",
             "{}", ";"])

        assert len(output.strip()) == 0, f'There should be no pep-8 errors!\n{output.strip()}'


class TestClinicalHistoryAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = CustomUser.objects.create_user(username='juan', password='1234', first_name='juan',
                                                    last_name='gomez', license='matricula #15433')
        self.patient = CustomUser.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                      password='12345', current_medic=self.medic, pk=1)
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history',
                                       status=models.PENDING, patient=self.patient)

    def test_get_all_clinical_histories(self):
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()['data']), 1)

    def test_create_clinical_history(self):
        data = {'date': datetime.now(), 'description': 'first clinical history',
                'status': 'P', 'patient_id': self.patient.pk}
        response = self.client.post('/api/v1/clinical_histories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalHistory.objects.count(), 2)


class TestClinicalSessionAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = CustomUser.objects.create_user(username='juan', password='1234', first_name='juan',
                                                    last_name='gomez', license='matricula #15433')
        self.patient = CustomUser.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                      password='12345', current_medic=self.medic, pk=1)
        self.clinical_history = ClinicalHistory.objects.create(date=datetime.now(),
                                                               description='a clinical history',
                                                               status=models.PENDING,
                                                               patient=self.patient)
        ClinicalSession.objects.create(date=datetime.now(),
                                       status=models.PENDING,
                                       clinical_history=self.clinical_history)

    def test_get_all_clinical_sessions(self):
        response = self.client.get('/api/v1/clinical_sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()['data']), 1)

    def test_create_clinical_session(self):
        data = {'date': datetime.now(), 'status': 'P', 'clinical_history': self.clinical_history.pk}
        response = self.client.post('/api/v1/clinical_sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalSession.objects.count(), 2)
