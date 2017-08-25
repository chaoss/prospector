# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from mptt.models import TreeForeignKey
from healthmeter.managers import get_natural_key_manager
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource


class Format(models.Model):
    name = models.CharField(max_length=50, unique=True)
    objects = get_natural_key_manager('name')

    def __unicode__(self):
        return self.name


@resource
class DataSource(models.Model):
    url = models.URLField(unique=True, max_length=1000)
    format = models.ForeignKey(Format, related_name='download_sources')
    last_updated = models.DateTimeField(null=True, blank=True, default=None)
    project = TreeForeignKey(Project, related_name='download_datasources')

    objects = get_natural_key_manager('url')

    class Meta:
        verbose_name = 'Download statistics source'

    def __unicode__(self):
        return self.url


class DataPoint(models.Model):
    source = models.ForeignKey(DataSource, related_name='datapoints')
    date = models.DateField()
    downloads = models.IntegerField()

    objects = get_natural_key_manager('source', 'date')

    class Meta:
        unique_together = ('source', 'date')

    def __unicode__(self):
        return u'{0} ({1}):{2}'.format(self.source, self.date, self.downloads)
