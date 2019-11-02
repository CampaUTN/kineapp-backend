import datetime
from freezegun import freeze_time

from kinesioapp.utils.test_utils import APITestCase
from users.models import User
from kinesioapp.models import Exercise
from users.tests.utils.mocks import NotificationManagerMock
from ...cron import SendExerciseReminder


@freeze_time("2019-11-05 08:00:00", tz_offset=-datetime.timedelta(hours=3, minutes=0))
class TestExerciseReminderNotification(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                              dni=39203040, birth_date=datetime.datetime.now(),
                                              firebase_device_id='medic_firebase_id')
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo', password='1234',
                                                dni=25000033, birth_date=datetime.datetime.now(), current_medic=self.medic,
                                                firebase_device_id='patient_firebase_id')
        NotificationManagerMock().reset()

    def _reset_notification_mock_and_send_notification(self) -> None:
        NotificationManagerMock().reset()
        SendExerciseReminder().do()

    def test_message_sent(self):
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.times_called, 1)

    def test_message_device_id(self):
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.sent_messages[0]['device_id'],
                          'patient_firebase_id')

    def test_message_title(self):
        exercise = Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.sent_messages[0]['title'],
                          f'Recordá hacer {exercise.name}!')

    def test_message_body(self):
        exercise = Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise',
                                           description='I am an exercise.')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.sent_messages[0]['body'],
                          exercise.description)

    def test_notification_is_sent_only_to_the_correct_user(self):
        User.objects.create_user(username='raul', password='1234', license='matricula #44523',
                                 dni=2452465, birth_date=datetime.datetime.now(),
                                 firebase_device_id='this_medic_should_not_receive_notifications')
        User.objects.create_user(username='sofia', first_name='sofia', password='1234',
                                 dni=5453545, birth_date=datetime.datetime.now(), current_medic=self.medic,
                                 firebase_device_id='this_patient_should_not_receive_notifications')
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.times_called, 1)
        self.assertEquals(NotificationManagerMock().firebase_connector.sent_messages[0]['device_id'], 'patient_firebase_id')

    def test_one_message_per_exercise_sent(self):
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise 1')
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise 2')
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise 3')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.times_called, 3)

    def test_do_not_send_notification_if_it_is_another_day(self):
        Exercise.objects.create(day=2, patient=self.patient.patient, name='exercise 2')
        self._reset_notification_mock_and_send_notification()
        self.assertEquals(NotificationManagerMock().firebase_connector.times_called, 0)

    def test_message_unsent_if_the_user_has_no_device_id(self):
        self.patient.firebase_device_id = None
        self.patient.save()
        Exercise.objects.create(day=1, patient=self.patient.patient, name='exercise')
        self._reset_notification_mock_and_send_notification()
        # The notification manager was cal, but the Firebase connector did not, because the user do not have the device_id
        self.assertEquals(NotificationManagerMock().times_called, 1)
        self.assertEquals(NotificationManagerMock().firebase_connector.times_called, 0)
