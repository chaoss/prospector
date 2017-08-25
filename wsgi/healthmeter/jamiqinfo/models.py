# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from mptt.models import TreeForeignKey, TreeManyToManyField

from healthmeter import fields, managers

from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource


class Credential(models.Model):
    username = models.CharField(max_length=255)
    password = fields.PlaintextPasswordField(max_length=255)

    objects = managers.get_natural_key_manager('username', 'password')

    class Meta:
        unique_together = ('username', 'password')

    def __unicode__(self):
        return self.username


@resource
class Topic(models.Model):
    credential = models.ForeignKey(Credential, related_name='topics')
    topic_id = models.IntegerField()
    name = models.CharField(max_length=300)
    last_updated = models.DateTimeField(blank=True, null=True, default=None)
    projects = TreeManyToManyField(Project, related_name='jamiq_topics',
                                   blank=True)

    objects = managers.get_natural_key_manager('credential', 'topic_id')

    class Meta:
        unique_together = ('credential', 'topic_id')
        verbose_name = 'Jamiq topic'

    def __unicode__(self):
        return u"{0}({1}) on {2}".format(self.name, self.topic_id,
                                         self.credential)


class DataPoint(models.Model):
    topic = models.ForeignKey(Topic, related_name='datapoints')

    datestamp = models.DateField()
    positive_sentiment_count = models.IntegerField()
    neutral_sentiment_count = models.IntegerField()
    negative_sentiment_count = models.IntegerField()

    objects = managers.QuerySetManager()

    class Meta:
        unique_together = ('topic', 'datestamp')

    def __unicode__(self):
        return u"{0}: {1}(+) {2}(=) {3}(-)".format(
            self.datestamp,
            self.positive_sentiment_count,
            self.neutral_sentiment_count,
            self.negative_sentiment_count)

    class QuerySet(models.query.QuerySet):
        def aggregate_by_date(self):
            Sum = models.Sum
            return self.values('datestamp') \
                       .annotate(positive=Sum('positive_sentiment_count'),
                                 negative=Sum('negative_sentiment_count'),
                                 neutral=Sum('neutral_sentiment_count'))
