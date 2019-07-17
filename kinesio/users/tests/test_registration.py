from django.test import TestCase
from rest_framework import status

from ..models import User
from .utils.mocks import GoogleUser as GoogleUserMock


class TestRegistration(TestCase):
    def test_missing_token(self):
        response = self.client.post('/api/v1/registration/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_possible_to_create_an_user_with_license_and_current_medic(self):
        data = {'google_token': 'i_am_a_working_token', 'license': '1234', 'current_medic': 1}
        response = self.client.post('/api/v1/registration/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_medic(self):
        data = {'google_token': 'i_am_a_working_token', 'license': '1234'}
        response = self.client.post('/api/v1/registration/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_medic_data_correctly_set(self):
        data = {'google_token': 'i_am_a_working_token', 'license': '1234'}
        response = self.client.post('/api/v1/registration/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().first_name, GoogleUserMock('fake_token').first_name)
        self.assertEqual(User.objects.get().medic.license, '1234')
