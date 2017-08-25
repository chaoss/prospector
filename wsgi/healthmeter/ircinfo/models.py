# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from healthmeter.managers import get_natural_key_manager, QuerySetManager
from healthmeter.participantinfo.models import Participant
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource
from mptt.models import TreeManyToManyField


class Server(models.Model):
    server_url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    objects = get_natural_key_manager('server_url')

    class Meta:
        verbose_name = "IRC Server"

    def __unicode__(self):
        return unicode(self.name)


class User(models.Model):
    participant = models.ForeignKey(Participant, related_name='irc_logins')
    nickname = models.CharField(max_length=20)
    server = models.ForeignKey(Server)

    objects = get_natural_key_manager('nickname', 'server')

    def __unicode__(self):
        return u'%s@%s' % (self.nickname, self.server)

    class Meta:
        unique_together = ('nickname', 'server')
        verbose_name = "IRC Login"


@resource
class Channel(models.Model):
    server = models.ForeignKey(Server, related_name='channels')
    name = models.CharField(max_length=255)

    projects = TreeManyToManyField(Project, related_name='irc_channels',
                                   blank=True)
    meeting_logs_url = models.CharField(max_length=255, null=True, blank=True)

    last_updated = models.DateTimeField(default=None, null=True, blank=True)

    objects = get_natural_key_manager('server', 'name')

    def save(self, *args, **kwargs):
        if self.meeting_logs_url == '':
            self.meeting_logs_url = None

        super(Channel, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('server', 'name')
        verbose_name = "IRC Channel"
        ordering = ('server__name', 'name')

    def __unicode__(self):
        return u'%s@%s' % (self.name, self.server)


class Meeting(models.Model):
    channel = models.ForeignKey(Channel, related_name='meetings')
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    objects = QuerySetManager()

    class Meta:
        ordering = ['time_start']
        unique_together = ('channel', 'time_start')
        verbose_name = "IRC Meeting"

    def __unicode__(self):
        return u'Meeting on %s at %s' % (self.channel, self.time_start)

    def get_messages(self):
        """Return Message instances for this meeting"""
        return self.channel.messages.filter(timestamp__gte=self.time_start,
                                            timestamp__lte=self.time_end)

    class QuerySet(models.query.QuerySet):
        def with_msg_count(self):
            return self.extra(
                select={'msg_count': ('select count(*) '
                                      'from ircinfo_message '
                                      'where timestamp >= time_start and '
                                      'timestamp <= time_end and '
                                      'ircinfo_message.channel_id='
                                      'ircinfo_meeting.channel_id')
                        })

        def with_participant_count(self):
            return self.extra(
                select={'participant_count': (
                        'select count (*) from ('
                        'select distinct(author_id) from '
                        'ircinfo_message where '
                        'timestamp >= time_start and '
                        'timestamp <= time_end and '
                        'ircinfo_message.channel_id='
                        'ircinfo_meeting.channel_id) subq')})


class Message(models.Model):
    author = models.ForeignKey(User)
    timestamp = models.DateTimeField()
    channel = models.ForeignKey(Channel, related_name='messages')

    def __unicode__(self):
        return u'Message by %s on %s at %s' % (self.author.nickname,
                                               self.channel,
                                               self.timestamp)
