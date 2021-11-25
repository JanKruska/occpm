from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.fields.related import ForeignKey

fs = FileSystemStorage()


class EventLog(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(storage=fs)
    hash = models.CharField(max_length=128)


class LogFiltering(models.Model):
    event_log_ref = ForeignKey(EventLog, on_delete=models.CASCADE)
    # name_of_log = _____ take from EventLog model?
    all_attributes = models.TextField()
    filtered_attributes = models.TextField()


class FilteredLog(EventLog):
    parent = ForeignKey(
        EventLog, on_delete=models.CASCADE, related_name="filtered_child"
    )
    filter = models.TextField(default="")


class AttributeFilteredLog(EventLog):
    parent = ForeignKey(
        FilteredLog, on_delete=models.CASCADE, related_name="attr_filtered_child"
    )
    filter = models.TextField(default="")
