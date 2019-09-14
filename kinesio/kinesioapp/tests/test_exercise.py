from rest_framework import status
from datetime import datetime

from kinesioapp.utils.test_utils import APITestCase
from users.models import User
from kinesioapp.models import Exercise


class TestGetExercisesOnPatientsAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                              dni=39203040, birth_date=datetime.now())
        self.another_medic = User.objects.create_user(username='juan55', license='matricula #5343',
                                                      dni=42203088, birth_date=datetime.now())
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo', password='1234',
                                                dni=25000033, birth_date=datetime.now(), current_medic=self.medic)
        User.objects.create_user(username='martin', current_medic=self.medic, dni=15505050, birth_date=datetime.now())

    def test_get_current_patient_without_exercises(self):
        self._log_in(self.patient, '1234')
        response = self.client.get(f'/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['exercises'], {'0': [], '1': [], '2': [], '3': [],
                                                                   '4': [], '5': [], '6': []})

    def test_get_current_patient_with_an_exercise(self):
        exercises = Exercise.objects.create_multiple(days=[1, 2, 3], patient=self.patient.patient, name='exercise')
        self._log_in(self.patient, '1234')
        response = self.client.get(f'/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['exercises'], {'0': [],
                                                                   '1': [{'description': '', 'id': exercises[0].id, 'name': 'exercise', 'video': None, 'done': False}],
                                                                   '2': [{'description': '', 'id': exercises[1].id, 'name': 'exercise', 'video': None, 'done': False}],
                                                                   '3': [{'description': '', 'id': exercises[2].id, 'name': 'exercise', 'video': None, 'done': False}],
                                                                   '4': [],
                                                                   '5': [],
                                                                   '6': []})

    def test_get_current_patient_with_two_exercises(self):
        first_exercises = Exercise.objects.create_multiple(days=[1, 2, 3], patient=self.patient.patient, name='exercise')
        second_exercises = Exercise.objects.create_multiple(days=[2, 4], patient=self.patient.patient, name='exercise 2')
        self._log_in(self.patient, '1234')
        response = self.client.get(f'/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['exercises'], {'0': [],
                                                                   '1': [{'description': '', 'id': first_exercises[0].id, 'name': 'exercise', 'video': None, 'done': False}],
                                                                   '2': [{'description': '', 'id': second_exercises[0].id, 'name': 'exercise 2', 'video': None, 'done': False},
                                                                         {'description': '', 'id': first_exercises[1].id, 'name': 'exercise', 'video': None, 'done': False}],
                                                                   '3': [{'description': '', 'id': first_exercises[2].id, 'name': 'exercise', 'video': None, 'done': False}],
                                                                   '4': [{'description': '', 'id': second_exercises[1].id, 'name': 'exercise 2', 'video': None, 'done': False}],
                                                                   '5': [],
                                                                   '6': []})


class TestExercisesAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                              dni=39203040, birth_date=datetime.now())
        self.another_medic = User.objects.create_user(username='juan55', license='matricula #5343',
                                                      dni=42203088, birth_date=datetime.now())
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo', password='1234',
                                                dni=25000033, birth_date=datetime.now(), current_medic=self.medic)
        User.objects.create_user(username='martin', current_medic=self.medic, dni=15505050, birth_date=datetime.now())

    def test_create_exercise_for_one_day(self):
        self._log_in(self.patient, '1234')
        data = {'name': 'Arm exercise', 'description': '....', 'days': [2], 'patient_id': self.patient.id}
        response = self.client.post('/api/v1/exercise/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.json()['data']), 1)
        self.assertEqual(Exercise.objects.count(), 1)

    def test_create_exercise_for_three_days(self):
        self._log_in(self.patient, '1234')
        data = {'name': 'Arm exercise', 'description': '....', 'days': [0, 4, 5], 'patient_id': self.patient.id}
        response = self.client.post('/api/v1/exercise/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.json()['data']), 3)
        self.assertEqual(Exercise.objects.count(), 3)

    def test_update_exercise(self):
        self._log_in(self.medic, '1234')
        exercise = Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        new_name = 'new name'
        response = self.client.patch(f'/api/v1/exercise/{exercise.id}', {'name': new_name}, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Exercise.objects.get(id=exercise.id).name, new_name)
        self.assertEquals(response.json()['name'], new_name)

    def test_delete_exercise(self):
        self._log_in(self.medic, '1234')
        exercise = Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        response = self.client.delete(f'/api/v1/exercise/{exercise.id}')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Exercise.objects.count(), 0)

    def test_fail_to_delete_a_exercise_of_other_patient(self):
        another_patient = User.objects.create_user(username='raul55', first_name='raul', password='0000',
                                                   dni=633836, birth_date=datetime.now(), current_medic=self.medic)
        self._log_in(another_patient, '0000')
        exercise = Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        response = self.client.delete(f'/api/v1/exercise/{exercise.id}')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(Exercise.objects.count(), 1)
