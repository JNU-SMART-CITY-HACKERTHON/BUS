from django.db import models


class Day(models.Model):
    day = models.CharField(max_length=10)
    rate = models.FloatField()

class Hour(models.Model):
    hour = models.IntegerField()
    rate = models.FloatField()

class Line(models.Model):
    line = models.CharField(max_length=30)
    rate = models.FloatField()
