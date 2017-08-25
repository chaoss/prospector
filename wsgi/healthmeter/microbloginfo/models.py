# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from mptt.models import TreeManyToManyField
from healthmeter.projectinfo.decorators import resource
from healthmeter.projectinfo.models import Project


class MicroblogProvider(models.Model):
    name = models.CharField(max_length=255, unique=True)
    username = models.TextField(default='', blank=True)
    password = models.TextField(default='', blank=True)

    def __unicode__(self):
        return self.name


@resource
class Microblog(models.Model):
    provider = models.ForeignKey(MicroblogProvider)
    handle = models.CharField(max_length=255, blank=False, unique=True)
    projects = TreeManyToManyField(Project, related_name='microblogs',
                                   blank=True)

    def __unicode__(self):
        return u'{0} on {1}'.format(self.handle, self.provider)


class MicroblogPost(models.Model):
    post_id = models.TextField()
    microblog = models.ForeignKey(Microblog, related_name='posts')

    timestamp = models.DateTimeField()
    content = models.TextField()
    reposts = models.IntegerField()

    class Meta:
        unique_together = ('microblog', 'post_id')
