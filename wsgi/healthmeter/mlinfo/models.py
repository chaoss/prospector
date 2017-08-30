# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from mptt.models import TreeForeignKey, TreeManyToManyField

from healthmeter.managers import get_natural_key_manager
from healthmeter.participantinfo.models import Participant
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource


class Purpose(models.Model):
    name = models.CharField(max_length=50, unique=True)
    objects = get_natural_key_manager('name')

    def __str__(self):
        return self.name


@resource
class MailingList(models.Model):
    posting_address = models.EmailField(unique=True)
    archive_url = models.CharField(max_length=10000)
    last_updated = models.DateTimeField(blank=True, null=True, default=None)

    projects = TreeManyToManyField(Project, through='MailingListProject',
                                   related_name='mailing_lists', blank=True)

    objects = get_natural_key_manager('posting_address')

    def __str__(self):
        return self.posting_address


class MailingListProject(models.Model):
    mailing_list = models.ForeignKey(MailingList)
    project = TreeForeignKey(Project)

    purpose = models.ForeignKey(Purpose)

    objects = get_natural_key_manager('project', 'mailing_list')

    def __str__(self):
        return "%s (%s): %s" % (self.project.name, self.purpose.name,
                                self.mailing_list.posting_address)

    class Meta:
        verbose_name = "Mailing List-Project relationship"
        unique_together = ('project', 'mailing_list')
        ordering = ('project__name',)


class Post(models.Model):
    author = models.ForeignKey(Participant, related_name='mailing_list_posts')
    timestamp = models.DateTimeField(db_index=True)
    subject = models.TextField()
    message_id = models.CharField(max_length=255, unique=True)

    mailing_lists = models.ManyToManyField(MailingList, related_name='posts')
    references = models.ManyToManyField('self', related_name='replies')

    objects = get_natural_key_manager('message_id')

    def __str__(self):
        return self.message_id
