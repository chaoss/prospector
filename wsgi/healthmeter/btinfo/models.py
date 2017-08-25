# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from healthmeter.managers import get_natural_key_manager
from healthmeter.participantinfo.models import Participant
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource
from healthmeter.fields import PlaintextPasswordField

from mptt.models import TreeManyToManyField


class Type(models.Model):
    name = models.CharField(max_length=10, unique=True)
    objects = get_natural_key_manager('name')

    def __unicode__(self):
        return unicode(self.name)


class BugTracker(models.Model):
    baseurl = models.URLField(max_length=255, unique=True)
    bt_type = models.ForeignKey(Type)

    username = models.CharField(max_length=255, null=True, blank=True)
    password = PlaintextPasswordField(max_length=255, null=True, blank=True)

    objects = get_natural_key_manager('baseurl')

    class Meta:
        verbose_name = "Bug Tracker"

    def __unicode__(self):
        return unicode(self.baseurl)


@resource
class BugNamespace(models.Model):
    bug_tracker = models.ForeignKey(BugTracker, related_name='namespaces')

    product = models.CharField(max_length=100, null=True, blank=True)
    component = models.CharField(max_length=100, null=True, blank=True)

    last_updated = models.DateTimeField(blank=True, null=True, default=None)

    projects = TreeManyToManyField(Project, related_name='bug_trackers',
                                   blank=True)

    objects = get_natural_key_manager('product', 'component', 'bug_tracker')

    def __unicode__(self):
        return u'(%s, %s) on %s' % (self.product, self.component,
                                    self.bug_tracker)

    class Meta:
        unique_together = ('product', 'component', 'bug_tracker')
        verbose_name = "Bug Namespace"


class Severity(models.Model):
    """
    List of bug severities healthmeter understands.

    +--------------+----------+---------+---------+--------------+
    |Health Monitor|RHBugzilla|Launchpad|Debbugs  |GNOME Bugzilla|
    |Severity Level|          |         |         |              |
    +--------------+----------+---------+---------+--------------+
    |              |          |Wishlist |wishlist |Enhancement   |
    |              |          +---------+---------+--------------+
    |1             |Low       |         |         |Trivial       |
    |              |          |Low      |minor    +--------------+
    |              |          |         |         |Minor         |
    +--------------+----------+---------+---------+--------------+
    |2             |Medium    |Medium   |normal   |Normal        |
    +--------------+----------+---------+---------+--------------+
    |3             |High      |High     |important|Major         |
    +--------------+----------+---------+---------+--------------+
    |              |          |         |serious  |              |
    |              |          |         +---------+Critical      |
    |4             |Urgent    |Critical |grave    |              |
    |              |          |         +---------+--------------+
    |              |          |         |critical |Blocker       |
    +--------------+----------+---------+---------+--------------+
    """
    name = models.CharField(max_length=20, unique=True)
    level = models.IntegerField(unique=True)

    objects = get_natural_key_manager('level')

    def __unicode__(self):
        return self.name


class Bug(models.Model):
    tracker_info = models.ForeignKey(BugNamespace, related_name='bugs')
    bug_id = models.CharField(max_length=20)
    close_date = models.DateTimeField(null=True)
    severity = models.ForeignKey(Severity, related_name='bugs', null=True)

    objects = get_natural_key_manager('tracker_info', 'bug_id')

    class Meta:
        unique_together = ('tracker_info', 'bug_id')

    def __unicode__(self):
        return u'Bug #%s on %s' % (self.bug_id,
                                   self.tracker_info)


class Comment(models.Model):
    bug = models.ForeignKey(Bug, related_name='comments')
    author = models.ForeignKey(Participant, related_name='bug_comments')

    timestamp = models.DateTimeField(db_index=True)
    comment_id = models.CharField(max_length=10)

    objects = get_natural_key_manager('bug', 'comment_id')

    def __unicode__(self):
        return u'Comment #%s on  %s' % (self.comment_id, self.bug)

    class Meta:
        unique_together = ('bug', 'comment_id')
