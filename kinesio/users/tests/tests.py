from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from json import dumps

from ..models import User
from ..serializers import UserSerializer
from .utils.mocks import GoogleUserMock
from unittest import mock


class TestObjectsSerializedInADictionary(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(username='juan', license='matricula #15433')

    def test_serializing_one_medic_returns_a_dictionary(self):
        serialized_objects_data = UserSerializer(User.objects.get(username='juan')).data
        self.assertNotEquals(dict, type(serialized_objects_data))

    def test_serializing_one_medic_does_not_create_data_key(self):
        serialized_objects_data = UserSerializer(User.objects.get(username='juan')).data
        self.assertTrue('data' not in serialized_objects_data)

    def test_serializing_multiple_medics_returns_a_dictionary(self):
        User.objects.create_user(username='maria76', license='matricula #1342')
        serialized_objects_data = UserSerializer(User.objects.medics(), many=True).data
        self.assertNotEquals(dict, type(serialized_objects_data))


class TestMedicsAPI(APITestCase):
    def setUp(self) -> None:
        User.objects.create_user(username='juan', license='matricula #15433')
        User.objects.create_user(username='maria22', license='matricula #44423')

    def test_get_all_medics(self):
        response = self.client.get('/api/v1/medics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)


class TestPatientsAPI(TestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', license='matricula #44423')
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo')
        User.objects.create_user(username='martin', current_medic=self.medic)

    def test_get_one_patient(self):
        response = self.client.get(f'/api/v1/patients/{self.patient.id}')
        breakpoint()
        self.assertEqual(response.json()['user']['first_name'], 'facundo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_patients(self):
        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)

    def test_update_one_patient(self):
        response = self.client.get(f'/api/v1/patients/{self.patient.id}')
        self.assertTrue(len(response.json().get('first_name')), 1)
        data = dumps({'first_name': 'facuUpdated'})
        response = self.client.patch('/api/v1/patients/1', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user']['first_name'], 'facuUpdated')


class TestGoogleLogin(TestCase):
    def test_missing_token(self):
        response = self.client.post('/api/v1/login_google/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        data = {'google_token': 'asd123sd123sad'}
        response = self.client.post('/api/v1/login_google/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestGoogleRegistration(TestCase):
    def test_missing_token(self):
        response = self.client.post('/api/v1/registration_google/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_possible_to_create_an_user_with_license_and_current_medic(self):
        data = {'google_token': 'i_am_a_working_token', 'license': '1234', 'current_medic': 1}
        response = self.client.post('/api/v1/registration_google/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_medic(self):
        with mock.patch('users.api.RegisterUserAPIView._get_google_user',
                        new=lambda google_token: GoogleUserMock(google_token)):
            data = {'google_token': 'i_am_a_working_token', 'license': '1234'}
            response = self.client.post('/api/v1/registration_google/', data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(User.objects.count(), 1)

    def test_medic_data_correctly_set(self):
        with mock.patch('users.api.RegisterUserAPIView._get_google_user',
                        new=lambda google_token: GoogleUserMock(google_token)):
            data = {'google_token': 'i_am_a_working_token', 'license': '1234'}
            response = self.client.post('/api/v1/registration_google/', data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(User.objects.get().first_name, GoogleUserMock('fake_token').first_name)
            self.assertEqual(User.objects.get().medic.license, '1234')
