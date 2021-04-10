from django.db import models


class Article(models.Model):
    name = models.TextField(max_length=32)
