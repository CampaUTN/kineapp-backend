from kinesioapp.utils.test_utils import APITestCase
from rest_framework import status
from datetime import datetime

from ..models import User
from kinesioapp.models import Exercise


class TestPatientsAPI(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                              dni=39203040, birth_date=datetime.now())
        self.another_medic = User.objects.create_user(username='juan55', license='matricula #5343',
                                                      dni=42203088, birth_date=datetime.now())
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo', password='1234',
                                                dni=25000033, birth_date=datetime.now(), current_medic=self.medic)
        User.objects.create_user(username='martin', current_medic=self.medic, dni=15505050, birth_date=datetime.now())
        self.patient_without_medic = User.objects.create_user(username='estela', first_name='estela', password='0000',
                                                              dni=4345338, birth_date=datetime.now())

    def test_get_current_patient(self):
        self._log_in(self.patient, '1234')
        response = self.client.get(f'/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], 'facundo')

    def test_patient_has_current_medic_first_and_last_name_when_serialized(self):
        self._log_in(self.patient, '1234')
        response = self.client.get(f'/api/v1/patients/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['patient']['current_medic']['first_name'], self.patient.patient.current_medic.first_name)
        self.assertEqual(response.json()['patient']['current_medic']['last_name'], self.patient.patient.current_medic.last_name)

    def test_get_all_patients_of_the_current_medic(self):
        self._log_in(self.medic, '1234')
        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['patients']), 2)

    def test_do_not_get_patients_from_other_medics(self):
        self._log_in(self.medic, '1234')
        User.objects.create_user(username='pepe23', dni=9044004, birth_date=datetime.now())
        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['patients']), 2)

    def test_update_patient_first_name(self):
        self._log_in(self.patient, '1234')
        data = {'first_name': 'raul'}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['first_name'], 'raul')
        # Check whether the db was properly updated or not
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.first_name, 'raul')

    def test_change_patient_current_medic_id(self):
        self._log_in(self.patient, '1234')
        data = {'patient': {'current_medic': {'id': self.another_medic.id}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['patient']['current_medic']['id'], self.another_medic.id)
        # Check whether the db was properly updated or not
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.patient.current_medic, self.another_medic)

    def test_assign_medic_for_the_first_time(self):
        self._log_in(self.patient_without_medic, '0000')
        data = {'patient': {'current_medic': {'id': self.another_medic.id}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['patient']['current_medic']['id'], self.another_medic.id)
        # Check whether the db was properly updated or not
        self.patient_without_medic.refresh_from_db()
        self.assertEqual(self.patient_without_medic.patient.current_medic.id, self.another_medic.id)

    def test_unset_medic_for_patient_using_id_zero(self):
        self._log_in(self.patient, '1234')
        data = {'patient': {'current_medic': {'id': 0}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['patient']['current_medic'], None)
        # Check whether the db was properly updated or not
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.patient.current_medic, None)

    def test_unset_medic_for_patient_using_id_minus_one(self):
        self._log_in(self.patient, '1234')
        data = {'patient': {'current_medic': {'id': -1}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response
        self.assertEqual(response.json()['patient']['current_medic'], None)
        # Check whether the db was properly updated or not
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.patient.current_medic, None)


class TestExerciseExistenceAfterPatientModification(APITestCase):
    def setUp(self) -> None:
        self.current_medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                                      dni=39203040, birth_date=datetime.now())
        self.another_medic = User.objects.create_user(username='juan55', license='matricula #5343',
                                                      dni=42203088, birth_date=datetime.now())
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo', password='1234',
                                                dni=25000033, birth_date=datetime.now(),
                                                current_medic=self.current_medic, firebase_device_id='6456282')
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        Exercise.objects.create(day=3, patient=self.patient.patient, name='another exercise')

    def test_exercises_are_not_deleted_if_the_patients_new_medic_is_the_same(self):
        self._log_in(self.patient, '1234')
        data = {'patient': {'current_medic': {'id': self.current_medic.id}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(self.patient.patient.exercises.count(), 2)

    def test_exercises_are_deleted_if_the_patient_change_its_medic(self):
        self._log_in(self.patient, '1234')
        data = {'patient': {'current_medic': {'id': self.another_medic.id}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(self.patient.patient.exercises.count(), 0)

    def test_exercises_are_deleted_if_the_patient_removes_its_medic(self):
        self._log_in(self.patient, '1234')
        data = {'patient': {'current_medic': {'id': -1}}}
        response = self.client.patch(f'/api/v1/patients/detail/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(self.patient.patient.exercises.count(), 0)
