from kinesioapp.utils.test_utils import APITestCase
from rest_framework import status
from datetime import datetime

from ..models import User, SecretQuestion


class TestContinueSession(APITestCase):
    def setUp(self) -> None:
        self.secret_question = SecretQuestion.objects.create(description='The answer is 1234?')
        self.answer = '1234'
        self.user = User.objects.create_user(username='facundo22', first_name='facundo', password=self.answer,
                                             secret_question=self.secret_question, dni=25000033,
                                             birth_date=datetime.now())

    def test_continue_session_with_valid_credentials(self):
        self._log_in(self.user, '1234')
        data = {'secret_question_id': self.secret_question.id, 'answer': self.answer}
        response = self.client.post(f'/api/v1/continue_session/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_continue_session_without_a_session(self):
        data = {'secret_question_id': self.secret_question.id, 'answer': self.answer}
        response = self.client.post(f'/api/v1/continue_session/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_continue_session_with_invalid_question_id(self):
        self._log_in(self.user, '1234')
        data = {'secret_question_id': self.secret_question.id + 1, 'answer': self.answer}
        response = self.client.post(f'/api/v1/continue_session/', data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_continue_session_with_invalid_answer(self):
        self._log_in(self.user, '1234')
        data = {'secret_question_id': self.secret_question.id, 'answer': self.answer + 'a'}
        response = self.client.post(f'/api/v1/continue_session/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_continue_session_with_invalid_question_id_and_answer(self):
        self._log_in(self.user, '1234')
        data = {'secret_question_id': self.secret_question.id + 100, 'answer': self.answer + 's'}
        response = self.client.post(f'/api/v1/continue_session/', data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
