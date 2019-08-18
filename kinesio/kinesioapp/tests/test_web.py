from django.test import TestCase
from rest_framework import status
from django.urls import reverse

from .. import models
from ..models import ClinicalSession
from users.models import User, SecretQuestion


class TestWebView(TestCase):
    def setUp(self) -> None:
        self.question = SecretQuestion.objects.create(description='Nombre de tu perro?')
        self.medic = User.objects.create_user(username='pepe', password='1234', license='12341234')
        self.patient = User.objects.create_user(username='juan', password='1234', current_medic=self.medic)
        self.session = ClinicalSession.objects.create(status=models.PENDING, patient=self.patient.patient)

    def test_index_page(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'layout/navbar.html')
        self.assertTemplateUsed(response, 'kinesioapp/index.html')

    def test_secret_question_page(self):
        url = reverse('secret_questions_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kinesioapp/login/secret_question.html')

    def test_after_login_flow(self):
        registration_data = {'google_token': 'token',
                             'secret_question_id': self.question.id,
                             'answer': 'perro',
                             'license': '12341234'}
        self.client.post('/api/v1/registration/', registration_data, format='json')
        login_data = {'google_token': 'token', 'secret_question_id': self.question.id, 'answer': 'perro'}
        response = self.client.post('/api/v1/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kinesioapp/users/sidebar.html')
        url = reverse('clinical_history_view')
        response = self.client.get(url + '?patient_id=' + str(self.patient.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kinesioapp/users/clinical_history.html')
        url = reverse('clinical_session_view')
        response = self.client.get(url + '?clinical_session_id=' + str(self.session.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kinesioapp/users/clinical_session.html')
