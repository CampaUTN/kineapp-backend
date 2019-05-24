from django.db import models


class Topic(models.Model):
    detail = models.CharField(max_length=50)


class Post(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    content = models.CharField(max_length=1000, unique=True)
    publication_date = models.DateTimeField(auto_now=True)
    topics = models.ManyToManyField(Topic)


