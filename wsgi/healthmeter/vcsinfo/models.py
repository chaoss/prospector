# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from mptt.models import TreeForeignKey

from healthmeter.participantinfo.models import Participant
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource


class Type(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "VCS types"
        verbose_name = "VCS type"

    def __str__(self):
        return self.name


@resource
class Repository(models.Model):
    type = models.ForeignKey(Type, related_name='repositories')
    project = TreeForeignKey(Project, related_name='repositories')
    url = models.CharField(max_length=10000, unique=True)
    last_updated = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        verbose_name_plural = "VCS repositories"
        verbose_name = "VCS repository"

    def __stre__(self):
        return self.url


class Committer(models.Model):
    participant = models.ForeignKey(Participant, related_name='committer_ids')
    repository = models.ForeignKey(Repository, related_name='committers')
    userid = models.CharField(max_length=200)

    class Meta:
        unique_together = ('userid', 'repository')

    def __str__(self):
        return self.userid


class Commit(models.Model):
    repository = models.ForeignKey(Repository, related_name='commits')
    commit_id = models.CharField(max_length=255)
    author = models.ForeignKey(Committer, related_name='commits')
    timestamp = models.DateTimeField(db_index=True)

    line_count = models.PositiveIntegerField(null=False, default=0)

    class Meta:
        verbose_name = "VCS commit"
        verbose_name_plural = "VCS commits"

        unique_together = ('repository', 'commit_id')

    def __str__(self):
        return '{0} on {1}'.format(self.commit_id, self.repository)
