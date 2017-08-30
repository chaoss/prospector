# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from healthmeter.managers import get_natural_key_manager
from healthmeter.participantinfo.models import Participant
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource
from mptt.models import TreeForeignKey, TreeManyToManyField


@resource
class Blog(models.Model):
    rss_url = models.URLField(max_length=255, unique=True)
    url = models.URLField(max_length=255, default='')
    projects = TreeManyToManyField(Project, related_name='blogs', blank=True)

    last_updated = models.DateTimeField(blank=True, null=True, default=None)

    objects = get_natural_key_manager('rss_url')

    def __str__(self):
        return self.url


class Post(models.Model):
    blog = models.ForeignKey(Blog, related_name='posts')
    timestamp = models.DateTimeField()
    author = models.ForeignKey(Participant, null=True)
    guid = models.CharField(max_length=255, default='')

    title = models.CharField(max_length=255, default='')

    class Meta:
        unique_together = ('blog', 'guid')

    def __str__(self):
        return '%s on %s' % (self.guid, self.blog)
