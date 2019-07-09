from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from json import dumps

from .models import CustomUser
from .serializers import CustomUserSerializer


class TestObjectsSerializedInADictionary(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(username='juan', license='matricula #15433')

    def test_serializing_one_medic_returns_a_dictionary(self):
        serialized_objects_data = CustomUserSerializer(CustomUser.objects.get(username='juan')).data
        self.assertNotEquals(dict, type(serialized_objects_data))

    def test_serializing_one_medic_does_not_create_data_key(self):
        serialized_objects_data = CustomUserSerializer(CustomUser.objects.get(username='juan')).data
        self.assertTrue('data' not in serialized_objects_data)

    def test_serializing_multiple_medics_returns_a_dictionary(self):
        CustomUser.objects.create_user(username='maria76', license='matricula #1342')
        serialized_objects_data = CustomUserSerializer(CustomUser.objects.medics(), many=True).data
        self.assertNotEquals(dict, type(serialized_objects_data))


class TestMedicsAPI(APITestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(username='juan', license='matricula #15433')
        CustomUser.objects.create_user(username='maria22', license='matricula #44423')

    def test_get_all_medics(self):
        response = self.client.get('/api/v1/medics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)


class TestPatientsAPI(TestCase):
    def setUp(self) -> None:
        self.medic = CustomUser.objects.create_user(username='maria22', license='matricula #44423')
        CustomUser.objects.create_user(pk=1, username='facundo22', first_name='facundo')
        CustomUser.objects.create_user(username='martin', current_medic=self.medic)

    def test_get_one_patient(self):
        response = self.client.get('/api/v1/patients/1')
        self.assertEqual(response.json().get('first_name'), 'facundo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_patients(self):
        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('data')), 2)

    def test_update_one_patient(self):
        response = self.client.get('/api/v1/patients/1')
        self.assertTrue(len(response.json().get('first_name')), 1)
        data = dumps({'first_name': 'facuUpdated'})
        response = self.client.patch('/api/v1/patients/1', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('first_name'), 'facuUpdated')
