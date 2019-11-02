from django_cron import CronJobBase, Schedule
import logging
from django.conf import settings
from datetime import date

from .models import Exercise


class ResetExerciseStatus(CronJobBase):
    RUN_AT_TIMES = ['23:59']

    schedule = Schedule(run_at_times=settings.RESET_EXERCISES_AT_TIMES)
    code = 'kinesioapp.reset_exercise_status'  # a unique code

    def do(self):
        if date.today().isoweekday() == 7:
            logging.info('Reset exercise status for all exercises... ')
            Exercise.objects.all().reset_status()
            logging.info('Done=False was set for all exercises.')
        else:
            logging.debug('Skipped exercise reset because today is not Sunday.')


class SendExerciseReminder(CronJobBase):
    RUN_AT_TIMES = ['08:00']

    schedule = Schedule(run_at_times=settings.RESET_EXERCISES_AT_TIMES)
    code = 'kinesioapp.reset_exercise_reminder'  # a unique code

    def do(self):
        logging.info('Reset exercise status for all exercises... ')
        exercises = Exercise.objects.all()
        for exercise in exercises:
            exercise.send_reminder_if_necessary()
        logging.info('Done=False was set for all exercises.')
