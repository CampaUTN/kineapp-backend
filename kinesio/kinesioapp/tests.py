import subprocess
from django.test import TestCase
from rest_framework import status
from datetime import datetime
from .utils.test_utils import APITestCase

from . import models
from .models import ClinicalHistory, ClinicalSession, Image
from users.models import User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile



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
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        self.clinical_history = ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history',
                                                               status=models.PENDING, patient=self.patient)

    def test_create_clinical_history(self):
        self._log_in(self.patient, '12345')
        data = {'date': datetime.now(), 'description': 'first clinical history',
                'status': 'P', 'patient_id': self.patient.pk}
        response = self.client.post('/api/v1/clinical_histories/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalHistory.objects.count(), 2)

    def test_get_clinical_history_for_a_patient(self):
        self._log_in(self.patient, '12345')
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 1)

    def test_get_clinical_history_for_a_medic(self):
        self._log_in(self.medic, '12345')
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 1)

    def test_get_multiple_clinical_histories_for_a_medic(self):
        self._log_in(self.medic, '12345')
        # Assign another patient to the medic from the fixture
        patient = User.objects.create_user(first_name='facundo', last_name='perez', username='another_patient',
                                           current_medic=self.medic)
        # Create a history for that patient
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history',
                                       status=models.PENDING, patient=patient)
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        # The medic should be able to access to the histories of both of their patients
        self.assertEquals(len(response.json()['data']), 2)

    def test_only_get_clinical_history_from_the_current_patient(self):
        self._log_in(self.patient, '12345')
        patient = User.objects.create_user(first_name='raul', last_name='gomez', username='rgomez',
                                           password='aaaaaaa', current_medic=self.medic)
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history',
                                       status=models.PENDING, patient=patient)
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data']), 1)

    def test_get_all_clinical_sessions_of_a_given_history(self):
        self._log_in(self.patient, '12345')
        self.clinical_session = ClinicalSession.objects.create(date=datetime.now(),
                                                               status=models.PENDING,
                                                               clinical_history=self.clinical_history)
        self.clinical_session = ClinicalSession.objects.create(date=datetime.now(),
                                                               status=models.PENDING,
                                                               clinical_history=self.clinical_history)
        self.clinical_session = ClinicalSession.objects.create(date=datetime.now(),
                                                               status=models.PENDING,
                                                               clinical_history=self.clinical_history)
        response = self.client.get('/api/v1/clinical_histories/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data'][0]['clinical_sessions']), 3)


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

    def test_create_clinical_session(self):
        data = {'date': datetime.now(), 'status': 'P', 'clinical_history_id': self.clinical_history.id}
        response = self.client.post('/api/v1/clinical_sessions/', data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalSession.objects.count(), 2)

    def test_upload_image(self):
        with open('/kinesio/kinesio/static/images/logo.png', 'rb') as file:
            data = {'content': file, 'date': datetime.now(),
                    'clinical_session_id': self.clinical_session.pk}
            response = self.client.post('/api/v1/image/', data)
        # Open the file again
        with open('/kinesio/kinesio/static/images/logo.png', 'rb') as file:
            content = file.read()
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.get().content.tobytes(), content)

    def test_delete_image(self):
        image = Image.objects.create(content=b'content', date=datetime.now(), clinical_session=self.clinical_session)
        response = self.client.delete(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Image.objects.count(), 0)
