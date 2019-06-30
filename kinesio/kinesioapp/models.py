from django.db import models


class CUser(models.Model):
    username = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateTimeField(auto_now=True)


class Medic(CUser):
    license = models.CharField(max_length=100)


class Patient(CUser):
    start_date = models.DateTimeField()
    finish_date = models.DateTimeField()


class Video(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(Medic, on_delete=models.CASCADE)


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    videos = models.ForeignKey(Video, on_delete=models.CASCADE)


class HomeworkExercise(models.Model):
    HOMEWORK_SESSION_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('D', 'DONE'),
        ('C', 'CANCELLED')
    ]

    date = models.DateTimeField()
    number_of_homework_session = models.IntegerField()
    status = models.CharField(max_length=100, choices=HOMEWORK_SESSION_STATUS_CHOICES, default='PENDING')
    exercises = models.ForeignKey(Exercise, on_delete=models.CASCADE)


class Homework(models.Model):
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    periodicity = models.IntegerField()
    exercises = models.ForeignKey(HomeworkExercise, on_delete=models.CASCADE)


class Image(models.Model):
    content = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date = models.DateTimeField()
    homework = models.OneToOneField(Homework, on_delete=models.CASCADE)


class ClinicalHistory(models.Model):
    CLINICAL_HISTORY_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('F', 'FINISHED'),
        ('C', 'CANCELLED')
    ]

    date = models.DateTimeField()
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=100, choices=CLINICAL_HISTORY_STATUS_CHOICES, default='PENDING')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medic = models.ForeignKey(Medic, on_delete=models.SET_NULL)


class Session(models.Model):
    SESSION_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('F', 'FINISHED'),
        ('C', 'CANCELLED')
    ]
    medic = models.ForeignKey(Medic, on_delete=models.SET_NULL)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=100, choices=SESSION_STATUS_CHOICES, default='PENDING')
    images = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)
    clinical_history = models.ForeignKey(ClinicalHistory, on_delete=models.CASCADE)



