import subprocess
from django.test import TestCase
from rest_framework import status
from datetime import datetime
from .utils.test_utils import APITestCase

from . import models
from .models import ClinicalHistory, ClinicalSession, Image
from users.models import User


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
        self.medic = User.objects.create_user(username='juan', password='1234', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history',
                                       status=models.PENDING, patient=self.patient)
        self._log_in(self.patient, '12345')

    def test_create_clinical_history(self):
        data = {'date': datetime.now(), 'description': 'first clinical history',
                'status': 'P', 'patient_id': self.patient.pk}
        response = self.client.post('/api/v1/clinical_histories/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalHistory.objects.count(), 2)

    def test_get_clinical_history(self):
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 1)

    def test_only_get_clinical_history_from_the_current_patient(self):
        patient = User.objects.create_user(first_name='raul', last_name='gomez', username='rgomez',
                                           password='aaaaaaa', current_medic=self.medic)
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history',
                                       status=models.PENDING, patient=patient)
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 1)


class TestClinicalSessionAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='1234', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        self.clinical_history = ClinicalHistory.objects.create(date=datetime.now(),
                                                               description='a clinical history',
                                                               status=models.PENDING,
                                                               patient=self.patient)
        self.clinical_session = ClinicalSession.objects.create(date=datetime.now(),
                                                               status=models.PENDING,
                                                               clinical_history=self.clinical_history)
        self._log_in(self.patient, '12345')

    def test_get_all_clinical_sessions(self):
        response = self.client.get('/api/v1/clinical_sessions/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 1)

    def test_create_clinical_session(self):
        data = {'date': datetime.now(), 'status': 'P', 'clinical_history': self.clinical_history.pk}
        response = self.client.post('/api/v1/clinical_sessions/', data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalSession.objects.count(), 2)

    def test_upload_image(self):
        data = {'content': 'reemplazarconunblob', 'date': datetime.now(),
                'clinical_session_id': self.clinical_session.pk}
        response = self.client.post('/api/v1/image/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Image.objects.count(), 1)

    def test_delete_image(self):
        data = {'content': 'reemplazarconunblob', 'date': datetime.now(),
                'clinical_session_id': self.clinical_session.pk}
        self.client.post('/api/v1/image/', data)
        image_created = Image.objects.get()
        self.assertEquals(Image.objects.count(), 1)
        response = self.client.delete(f'/api/v1/image/{image_created.id}')
        self.assertEquals(Image.objects.count(), 0)
