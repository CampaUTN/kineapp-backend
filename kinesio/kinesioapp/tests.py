import subprocess
from django.test import TestCase
from rest_framework.test import APITestCase
from . import models
from .models import Medic, ClinicalHistory, ClinicalSession
from .serializers import MedicSerializer
from rest_framework import status
from datetime import datetime


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
        ClinicalHistory.objects.create(date=datetime.now(), description='a clinical history', status=models.PENDING,
                                       medic=self.medic, patient=None)

    def test_get_all_clinical_histories(self):
        response = self.client.get('/api/v1/clinical_histories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()['data']), 1)

    def test_create_clinical_history(self):
        data = {'date': datetime.now(), 'description': 'first clinical history',
                'status': 'pending', 'medic': self.medic.pk, 'patient': None}
        response = self.client.post('/api/v1/clinical_histories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalHistory.objects.count(), 2)


class TestClinicalSessionAPI(APITestCase):
    def setUp(self) -> None:
        medic = Medic.objects.create(username='juan',
                                     password='1234',
                                     name='juan',
                                     last_name='gomez',
                                     license='matricula #15433')
        self.clinical_history = ClinicalHistory.objects.create(date=datetime.now(),
                                                               description='a clinical history',
                                                               status=models.PENDING,
                                                               medic=medic,
                                                               patient=None)
        ClinicalSession.objects.create(date=datetime.now(),
                                       status=models.PENDING,
                                       clinical_history=self.clinical_history)

    def test_get_all_clinical_sessions(self):
        response = self.client.get('/api/v1/clinical_sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()['data']), 1)

    def test_create_clinical_session(self):
        data = {'date': datetime.now(), 'status': 'pending', 'clinical_history': self.clinical_history.pk}
        response = self.client.post('/api/v1/clinical_sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ClinicalSession.objects.count(), 2)
