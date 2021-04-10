from django.db import models


class Article(models.Model):
    title = models.TextField()
    body = models.TextField()
