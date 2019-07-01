import subprocess
from django.test import TestCase
from .models import Medic, Patient
from rest_framework import status
from datetime import datetime
from json import dumps


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
        assert len(output.strip()) == 0, 'There should be no pep-8 errors!\n' + str(output.strip())


class TestPatientsAPI(TestCase):
    def setUp(self) -> None:
        self.medic = Medic.objects.create(name='martin', last_name='gonzales', username='tincho', password='12345',
                                          license='test1')
        patient1 = Patient.objects.create(pk=1, name='facundo', last_name='perez', username='pepe', password='12345',
                                          current_medic=self.medic, start_date=datetime.now(),
                                          finish_date=datetime.now())
        patient2 = Patient.objects.create(name='federico', last_name='perez', username='fede', password='12345',
                                          start_date=datetime.now(), finish_date=datetime.now())

    def test_get_one_patient(self):
        response = self.client.get('/api/v1/patients/1')
        self.assertTrue(response.json().get('name'), 'facundo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_one_patient(self):
        response = self.client.delete('/api/v1/patients/1')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Patient.objects.count(), 1)

    def test_get_all_patients(self):
        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()), 2)

    def test_create_patient(self):
        data = {'name': 'francisco', 'last_name': 'Bergoglio', 'username': 'papa', 'current_medic': self.medic.pk,
                'start_date': datetime.now(), 'finish_date': datetime.now()}
        response = self.client.post('/api/v1/patients/', data, format='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Patient.objects.count(), 3)

    def test_update_one_patient(self):
        response = self.client.get('/api/v1/patients/1')
        self.assertTrue(len(response.json().get('name')), 1)
        data = dumps({'name': 'facuUpdated'})
        response = self.client.patch('/api/v1/patients/1', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json().get('name'), 'facuUpdated')
