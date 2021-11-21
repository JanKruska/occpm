from django.db import models
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage()


class EventLog(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(storage=fs)
    hash = models.CharField(max_length=128)
