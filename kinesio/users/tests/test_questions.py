from django.test import TestCase
from rest_framework import status
from json import dumps

from ..models import User, SecretQuestion


class TestQuestionsAPI(TestCase):
    def setUp(self) -> None:
        self.question = SecretQuestion.objects.create(description='Cual es tu comida favorita?')
        SecretQuestion.objects.create(description='Como se llama tu perro?')

    def test_get_one_question(self):
        response = self.client.get(f'/api/v1/secret_questions/{self.question.id}')
        self.assertEqual(response.json().get('description'), 'Cual es tu comida favorita?')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_questions(self):
        response = self.client.get('/api/v1/secret_questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('data')), 2)

    def test_update_one_questions(self):
        response = self.client.get(f'/api/v1/secret_questions/{self.question.id}')
        self.assertTrue(len(response.json().get('description')), 1)
        data = dumps({'description': 'Updated comida favorita?'})
        response = self.client.patch(f'/api/v1/secret_questions/{self.question.id}', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('description'), 'Updated comida favorita?')


class CheckAnswerAPI(TestCase):
    def setUp(self) -> None:
        self.question = SecretQuestion.objects.create(description='Cual es tu color favorito?')
        self.user = User.objects.create_user(username='user', secret_question_id=self.question.id)
        self.user.set_password('rojo')
        self.user.save()

    def test_check_valid_question_answer(self):
        response = self.client.post('/api/v1/login/', {
            "username": self.user.username,
            "secret_question_id": self.question.id,
            "answer": "rojo"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), 'Logged in')

    def test_check_wrong_question_answer(self):
        response = self.client.post('/api/v1/login/', {
            "username": self.user.username,
            "secret_question_id": self.question.id,
            "answer": "azul"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_answer_not_found_user_id(self):
        response = self.client.post('/api/v1/login/', {
            "username": "anotherUser",
            "secret_question_id": self.question.id,
            "answer": "rojo"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("message"), "User not found")

    def test_answer_not_found_question_id(self):
        response = self.client.post('/api/v1/login/', {
            "username": self.user.username,
            "secret_question_id": 879879,
            "answer": "rojo"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("message"), "Question not found")
