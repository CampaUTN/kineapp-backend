from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from json import dumps

from .models import CustomUser, SecretQuestion
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
        p = CustomUser.objects.create_user(username='maria22', secret_question_id=self.question.id)
        p.set_password('rojo')
        self.patient = p

    def test_check_valid_question_answer(self):
        print("******************************************************")
        print(self.patient.id)
        print(self.question.id,)
        response = self.client.post('/api/v1/secret_questions/', {
            "user_id": self.patient.id,
            "secret_question_id": self.question.id,
            "answer": 'rojo'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('compare'), True)


    def test_check_wrong_question_answer(self):
        response = self.client.post('/api/v1/secret_questions/', {
            "user_id": self.patient.id,
            "secret_question_id": self.question.id,
            "answer": "azul"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('compare'), 'false')

    def test_answer_not_found_user_id(self):
        response = self.client.post('/api/v1/secret_questions/', {
            "user_id": 89879,
            "secret_question_id": self.question.id,
            "answer": "rojo"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "User not found")

    def test_answer_not_found_question_id(self):
        response = self.client.post('/api/v1/secret_questions/', {
            "user_id": self.patient.id,
            "secret_question_id": 879879,
            "answer": "rojo"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "User not found")
