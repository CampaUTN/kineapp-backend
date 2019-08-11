import subprocess
from django.test import TestCase
from rest_framework import status
from datetime import datetime
from .utils.test_utils import APITestCase

from . import models
from .models import ClinicalSession, Image
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


class TestClinicalSessionOnPatientAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        User.objects.create_user(first_name='maria', last_name='gomez', username='mgomez')
        ClinicalSession.objects.create(date=datetime.now(),
                                       status=models.PENDING,
                                       patient=self.patient.patient)
        ClinicalSession.objects.create(date=datetime.now(),
                                       status=models.PENDING,
                                       patient=self.patient.patient)
        ClinicalSession.objects.create(date=datetime.now(),
                                       status=models.PENDING,
                                       patient=self.patient.patient)

    def test_get_clinical_sessions_for_a_patient(self):
        self._log_in(self.patient, '12345')
        response = self.client.get(f'/api/v1/patients/{self.patient.id}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['patient']['sessions']), 3)

    def test_get_clinical_sessions_of_a_patient_of_the_medic(self):
        self._log_in(self.medic, '12345')
        response = self.client.get(f'/api/v1/patients/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()['data'][0]['patient']['sessions']), 3)


class TestClinicalSessionCreateAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        self._log_in(self.medic, '12345')

    def test_create_clinical_session(self):
        data = {'date': datetime.now(), 'status': 'P', 'patient_id': self.patient.id}
        response = self.client.post('/api/v1/clinical_sessions/', data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalSession.objects.count(), 1)


class TestImageAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='12345', first_name='juan',
                                              last_name='gomez', license='matricula #15433')
        self.patient = User.objects.create_user(first_name='facundo', last_name='perez', username='pepe',
                                                password='12345', current_medic=self.medic)
        self.clinical_session = ClinicalSession.objects.create(date=datetime.now(),
                                                               status=models.PENDING,
                                                               patient=self.patient.patient)
        self._log_in(self.medic, '12345')

    def test_image_data_on_database_is_different_than_input(self):
        content = b'content'
        image = Image.objects.create(content=content, clinical_session=self.clinical_session)
        self.assertNotEquals(image._content, content)

    def test_create_image(self):
        with open('/kinesio/kinesio/static/images/logo.png', 'rb') as file:
            data = {'content': file, 'clinical_session_id': self.clinical_session.pk}
            response = self.client.post('/api/v1/image/', data)
        # Open the file again
        with open('/kinesio/kinesio/static/images/logo.png', 'rb') as file:
            content = file.read()
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.get().content, content)

    def test_delete_image(self):
        image = Image.objects.create(content=b'content', clinical_session=self.clinical_session)
        response = self.client.delete(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Image.objects.count(), 0)

    def test_get_image(self):
        with open('/kinesio/kinesio/static/images/logo.png', 'rb') as file:
            content = file.read()
        image = Image.objects.create(content=content, clinical_session=self.clinical_session)
        response = self.client.get(f'/api/v1/image/{image.id}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(type(response.content), bytes)
        self.assertEquals(response.content, content)
