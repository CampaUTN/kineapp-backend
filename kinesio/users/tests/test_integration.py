from kinesioapp.utils.test_utils import APITestCase
from rest_framework import status
from ..models import User, SecretQuestion
from rest_framework.authtoken.models import Token


class TestIntegration(APITestCase):
    def setUp(self) -> None:
        self.question = SecretQuestion.objects.create(description='Cual es tu color favorito?')
        self.medic = User.objects.create_user(username='juan', password='1234', license='matricula #15433')

    def test_integration_patient_registration_loging_and_information_update(self):
        # Register the user
        registration_data = {'google_token': 'i_am_a_working_token',
                             'secret_question_id': self.question.id,
                             'answer': 'azul'}
        response = self.client.post('/api/v1/registration/', registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

        # Try to log the user in with a wrong answer
        login_data = {'google_token': 'i_am_a_working_token', 'secret_question_id': self.question.id, 'answer': 'verde'}
        response = self.client.post('/api/v1/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        # Try to update the user's personal information, but fail due to user not being logged in.
        update_data = {'first_name': 'raul'}
        response = self.client.patch(f'/api/v1/patients/detail/',
                                     update_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to log the user in with the valid answer
        login_data = {'google_token': 'i_am_a_working_token', 'secret_question_id': self.question.id, 'answer': 'azul'}
        response = self.client.post('/api/v1/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()['token']  # Save the token for later

        # Log the patient user in.
        # If this works, it is because the token was correctly created and associated to the user
        self._log_in(Token.objects.get(key=token).user, 'azul')

        # Try to update the user's personal information again and assign a medic. Now it should be working
        update_data = {'first_name': 'raul', 'patient': {'current_medic_id': self.medic.id}}
        response = self.client.patch(f'/api/v1/patients/detail/',
                                     update_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the user data and check whether it is updated or not
        response = self.client.get(f'/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], 'raul')
        self.assertEqual(response.json()['patient']['current_medic_id'], self.medic.id)
