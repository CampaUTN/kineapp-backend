from rest_framework.test import APITestCase
from rest_framework import status

from ..models import User


class TestMedicsAPI(APITestCase):
    def setUp(self) -> None:
        User.objects.create_user(username='juan', license='matricula #15433')
        User.objects.create_user(username='maria22', license='matricula #44423')

    def test_get_all_medics(self):
        response = self.client.get('/api/v1/medics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)
