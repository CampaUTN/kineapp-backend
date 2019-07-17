from django.test import TestCase
from rest_framework import status


class TestGoogleLogin(TestCase):
    def test_missing_token(self):
        response = self.client.post('/api/v1/user_exists/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        data = {'google_token': 'asd123sd123sad'}
        response = self.client.post('/api/v1/user_exists/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
