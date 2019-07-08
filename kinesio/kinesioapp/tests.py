import subprocess
from django.test import TestCase

from rest_framework.test import APITestCase
from . import models
from .models import Medic, ClinicalHistory, ClinicalSession, Patient
from .serializers import MedicSerializer
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

        assert len(output.strip()) == 0, f'There should be no pep-8 errors!\n{output.strip()}'


class TestObjectsSerializedInADictionary(TestCase):
    def setUp(self) -> None:
        Medic.objects.create(username='juan', password='1234', name='juan',
                             last_name='gomez', license='matricula #15433')

    def test_serializing_one_medic_returns_a_dictionary(self):
        serialized_objects_data = MedicSerializer(Medic.objects.get(name='juan')).data
        self.assertNotEquals(dict, type(serialized_objects_data))

    def test_serializing_one_medic_does_not_create_data_key(self):
        serialized_objects_data = MedicSerializer(Medic.objects.get(name='juan')).data
        self.assertTrue('data' not in serialized_objects_data)

    def test_serializing_multiple_medics_returns_a_dictionary(self):
        Medic.objects.create(username='maria76', password='7070', name='maria',
                             last_name='martinez vega', license='matricula #1342')
        serialized_objects_data = MedicSerializer(Medic.objects.all(), many=True).data
        self.assertNotEquals(dict, type(serialized_objects_data))


class TestMedicsAPI(APITestCase):
    def setUp(self) -> None:
        Medic.objects.create(username='juan', password='1234', name='juan',
                             last_name='gomez', license='matricula #15433')
        Medic.objects.create(username='maria22', password='0000000', name='maria',
                             last_name='ramirez', license='matricula #73234')

    def test_get_all_medics(self):
        response = self.client.get('/api/v1/medics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()['data']), 2)

    def test_create_medic_via_api(self):
        data = {'username': 'pepe', 'name': 'pepe', 'last_name': 'gomez', 'license': 'matricula #1234A'}
        response = self.client.post('/api/v1/medics/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Medic.objects.count(), 3)


class TestClinicalHistoryAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = Medic.objects.create(username='juan', password='1234', name='juan',
                                          last_name='gomez', license='matricula #15433')
        self.patient = Patient.objects.create(pk=1, name='facundo', last_name='perez', username='pepe', password='12345',
                                              current_medic=self.medic, start_date=datetime.now(),
                                              finish_date=datetime.now())
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history', status=models.PENDING,
                                       patient=self.patient)

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
        self.medic = Medic.objects.create(username='juan',
                                          password='1234',
                                          name='juan',
                                          last_name='gomez',
                                          license='matricula #15433')
        self.patient = Patient.objects.create(pk=1, name='facundo', last_name='perez', username='pepe', password='12345',
                                              current_medic=self.medic, start_date=datetime.now(),
                                              finish_date=datetime.now())
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


class TestPatientsAPI(TestCase):
    def setUp(self) -> None:
        self.medic = Medic.objects.create(name='martin', last_name='gonzales', username='tincho', password='12345',
                                          license='test1')
        Patient.objects.create(pk=1, name='facundo', last_name='perez', username='pepe', password='12345',
                               current_medic=self.medic, start_date=datetime.now(),
                               finish_date=datetime.now())
        Patient.objects.create(name='federico', last_name='perez', username='fede', password='12345',
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


class TestGoogleToken(TestCase):
    def test_missing_token(self):
        response = self.client.post('/api/v1/login_google/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_token(self):
        data = {'google_token': 'asd123sd123sad'}
        response = self.client.post('/api/v1/login_google/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
