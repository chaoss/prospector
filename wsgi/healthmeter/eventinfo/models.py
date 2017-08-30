from django.db import models
from mptt.models import TreeForeignKey
from healthmeter.projectinfo.models import Project


class Event(models.Model):
    project = TreeForeignKey(Project)
    desc = models.CharField(max_length=255)
    date_start = models.DateField()
    date_end = models.DateField()

    def clean(self):
        """Check that date_end is after date_start"""
        if self.date_start > self.date_end:
            raise ValidationError("Ending date must come after starting date "
                                  "of event")

    def __str__(self):
        return '%s (%s-%s)' % (self.desc, self.date_start, self.date_end)
