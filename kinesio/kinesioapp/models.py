from django.db import models

class CUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    dayOfBirth = models.DateTimeField()
    

class Medic(CUser):
    license = models.CharField(max_length=100)

class Patient(CUser):
    startDate = models.DateTimeField()
    finishDate = models.DateTimeField()

class Video(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(Medic, on_delete=models.CASCADE)

class Exercise(models.Model):
    name = models.CharField(max_length=255)
    videos = models.ForeignKey(Video, on_delete=models.CASCADE)

class HomeworkExercise(models.Model):
    HOMEWORK_SESSION_STATUS_CHOICES = [
        ('P','PENDING'),
        ('D','DONE'),
        ('C','CANCELLED')
    ]

    date = models.DateTimeField()
    numberOfHomeworkSession = models.IntegerField()
    status = models.CharField(max_length=100, choices=HOMEWORK_SESSION_STATUS_CHOICES, default= 'PENDING')
    exercises = models.ForeignKey(Exercise, on_delete=models.CASCADE)

class Homework(models.Model):
    fromDate = models.DateTimeField()
    toDate = models.DateTimeField()
    periodiciy = models.IntegerField()
    exercises = models.ForeignKey(HomeworkExercise, on_delete=models.CASCADE)
    
class Image(models.Model):
    content = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date = models.DateTimeField()
    homework = models.OneToOneField(Homework, on_delete=models.CASCADE)

class Session(models.Model):
    SESSION_STATUS_CHOICES = [
        ('P','PENDING'),
        ('F','FINISHED'),
        ('C','CANCELLED')
    ]
    medic = models.ForeignKey(Medic, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=100, choices=SESSION_STATUS_CHOICES, default= 'PENDING')
    images = models.ForeignKey(Image, on_delete=models.CASCADE, blank=True, null=True)


class ClinicalHistory(models.Model):
    CLINICAL_HISTORY_STATUS_CHOICES = [
        ('P','PENDING'),
        ('F','FINISHED'),
        ('C','CANCELLED')
    ]

    date = models.DateTimeField()
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=100, choices=CLINICAL_HISTORY_STATUS_CHOICES, default= 'PENDING')
    sessions = models.ForeignKey(Session, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medic = models.ForeignKey(Medic, on_delete=models.CASCADE)
    

