""" These test suites test different endpoints.
    They are designed to ensure that there are no problems with the picture on the back-end side, due to some
    bugs related to profile pictures on the integrations between back and mobile. """
from kinesioapp.utils.test_utils import APITestCase
from rest_framework import status
from django.utils import timezone

from ..models import User


class ProfilePictureModelTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='juan', password='1234', license='matricula #15433',
                                             dni=39203040, birth_date=timezone.now(), _picture_base64=b'initial')

    def test_picture_base64_property_is_working(self):
        self.user.refresh_from_db()
        self.assertEqual(self.user.picture_base64, 'initial')

    def test_change_picture_of_user_instance_to_string(self):
        self.user.change_profile_picture('another')
        self.user.refresh_from_db()
        self.assertEqual(self.user.picture_base64, 'another')

    def test_change_picture_of_user_instance_to_bytes(self):
        self.user.change_profile_picture(b'another')
        self.user.refresh_from_db()
        self.assertEqual(self.user.picture_base64, 'another')


class ProfilePictureAPITest(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='juan', password='1234', license='matricula #15433',
                                              dni=39203040, birth_date=timezone.now(), _picture_base64=b'nice_picture')
        self.patient = User.objects.create_user(username='juan2', password='1234', current_medic=self.medic,
                                                dni=543454, birth_date=timezone.now(), _picture_base64=b'another picture')

    def test_picture_is_returned_within_a_medic_user(self):
        self._log_in(self.medic, '1234')
        response = self.client.get('/api/v1/medics/detail', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['picture_base64'], 'nice_picture')

    def test_picture_is_returned_within_a_patient_user(self):
        self._log_in(self.patient, '1234')
        response = self.client.get('/api/v1/patients/detail', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['picture_base64'], 'another picture')

    def test_update_medic_user_picture(self):
        self._log_in(self.medic, '1234')
        data = {'picture_base64': 'new'}
        response = self.client.patch('/api/v1/medics/detail', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['picture_base64'], 'new')
        # Check whether the db was properly updated or not
        self.medic.refresh_from_db()
        self.assertEqual(self.medic.picture_base64, 'new')

    def test_update_patient_user_picture(self):
        self._log_in(self.patient, '1234')
        data = {'picture_base64': 'new'}
        response = self.client.patch('/api/v1/patients/detail', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['picture_base64'], 'new')
        # Check whether the db was properly updated or not
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.picture_base64, 'new')
