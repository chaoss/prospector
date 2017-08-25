# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.db import models
from healthmeter import fields
from healthmeter.managers import get_natural_key_manager
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource

from mptt.models import TreeForeignKey


class Credential(models.Model):
    """Credentials for retrieving CSVs"""
    username = models.CharField(max_length=255)
    password = fields.PlaintextPasswordField(max_length=255)

    objects = get_natural_key_manager('username', 'password')

    def __unicode__(self):
        return self.username

    class Meta:
        unique_together = ('username', 'password')


@resource
class Query(models.Model):
    keyword = models.CharField(max_length=300, unique=True)
    last_updated = models.DateTimeField(blank=True, null=True, default=None)
    project = TreeForeignKey(Project, related_name='gtrends_queries')

    objects = get_natural_key_manager('keyword')

    class Meta:
        verbose_name = 'Google trend query'
        verbose_name_plural = 'Google trend queries'

    def __unicode__(self):
        return self.keyword


class DataPoint(models.Model):
    keyword = models.ForeignKey(Query, related_name='datapoints')
    start = models.DateField()
    end = models.DateField()
    count = models.PositiveIntegerField()

    objects = get_natural_key_manager('keyword', 'start', 'end')

    class Meta:
        unique_together = ('keyword', 'start', 'end')

    def __unicode__(self):
        return u"{0}-{1}: {2}".format(self.start, self.end, self.count)
