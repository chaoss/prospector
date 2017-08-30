# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import colorful.fields
import datetime
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField
from mptt.managers import TreeManager

from preferences.models import Preferences
from jsonfield.fields import JSONField

import hashlib
import itertools
import json
import logging

from healthmeter.participantinfo.models import *
from healthmeter.projectinfo import models as projectmodels
from healthmeter.vcsinfo import models as vcsmodels
from healthmeter.mlinfo import models as mlmodels
from healthmeter.btinfo import models as btmodels
from healthmeter.eventinfo import models as eventmodels
from healthmeter.bloginfo import models as blogmodels

from healthmeter.managers import (ProxyTreeManager, QuerySetManager,
                                  get_natural_key_manager)

from healthmeter.utils import djcached
from .utils.cache import cached_property, djcached_by_project
from .utils.containers import AttrDict
from .utils.stats import max_or_none
from .managers import ProjectQuerySet, ProjectManager
from .metrics.constants import score_to_colour


logger = logging.getLogger(__name__)


class Options(Preferences):
    class Meta:
        verbose_name = 'Options'
        verbose_name_plural = 'Options'

    highlight_domain = models.ForeignKey(EmailDomain, null=True, default=None)


class Project(projectmodels.Project):
    objects = ProjectManager()
    QuerySet = ProjectQuerySet

    class Meta(projectmodels.Project.Meta):
        proxy = True

    def get_absolute_url(self):
        return reverse('hmeter_frontend:project:detail',
                       kwargs={'pk': self.id})

    @property
    def all_projects(self):
        return self.get_descendants(include_self=True)

    @property
    def all_releases(self):
        return projectmodels.Release.objects.filter(
            project__in=self.all_projects)

    @property
    def all_licenses(self):
        return projectmodels.License.objects.filter(
            projects__in=self.all_projects).distinct('id')

    @property
    def all_bug_trackers(self):
        return btmodels.BugNamespace.objects.filter(
            projects__in=self.all_projects)

    @property
    def all_vcs_repositories(self):
        return vcsmodels.Repository.objects.filter(
            project__in=self.all_projects)

    @property
    def all_mailing_lists(self):
        return mlmodels.MailingList.objects.filter(
            projects__in=self.all_projects)

    @property
    def all_blogs(self):
        return blogmodels.Blog.objects.filter(projects__in=self.all_projects)

    @cached_property
    @djcached_by_project('start_date', 24 * 3600)
    def smart_start_date(self):
        if self.start_date:
            return self.start_date

        try:
            return vcsmodels.Commit \
                .objects \
                .filter(
                    repository__project__in=self.all_projects
                ) \
                .aggregate(start_date=models.Min('timestamp'))['start_date'] \
                .date()
        except (KeyError, AttributeError):
            return None

    @property
    @djcached_by_project('last_updated', 24 * 3600)
    def last_updated(self):
        projects = self.all_projects

        querysets = (self.all_vcs_repositories,
                     self.all_bug_trackers,
                     self.all_mailing_lists,
                     self.all_blogs)

        last_updated_dates = (qs.aggregate(lu=models.Max('last_updated'))['lu']
                              for qs in querysets)
        return max_or_none(last_updated_dates)

    @cached_property
    @djcached_by_project('last_activity', 24 * 3600)
    def last_activity(self):
        projects = self.all_projects

        extra_args = {}

        def update_timestamp(new_timestamp):
            if new_timestamp is None:
                return

            try:
                extra_args['timestamp__gt'] = max(
                    extra_args['timestamp__gt'],
                    new_timestamp)
            except KeyError:
                extra_args['timestamp__gt'] = new_timestamp

        timestamp = vcsmodels.Commit.objects \
            .filter(repository__project__in=projects,
                    **extra_args) \
            .aggregate(timestamp=models.Max('timestamp'))['timestamp']
        update_timestamp(timestamp)

        timestamp = mlmodels.Post.objects \
            .filter(mailing_lists__projects__in=projects,
                    **extra_args) \
            .aggregate(timestamp=models.Max('timestamp'))['timestamp']
        update_timestamp(timestamp)

        timestamp = btmodels.Comment.objects \
            .filter(bug__tracker_info__projects__in=projects,
                    **extra_args) \
            .aggregate(timestamp=models.Max('timestamp'))['timestamp']
        update_timestamp(timestamp)

        timestamp = blogmodels.Post.objects \
            .filter(blog__projects__in=projects, **extra_args) \
            .aggregate(timestamp=models.Max('timestamp'))['timestamp']
        update_timestamp(timestamp)

        most_recent_date = extra_args.get('timestamp__gt', None)

        return most_recent_date

    @property
    def score(self):
        return self.get_score()

    def __gen_score_cache_key(self, start=None, end=None, **kwargs):
        epoch = datetime.datetime.utcfromtimestamp(0)

        def td2epoch(td):
            return td.days * 24 * 3600 + td.seconds

        if start:
            start = int(td2epoch(start - epoch))

        if end:
            end = int(td2epoch(end - epoch))

        return 'project:{0}:health_score:{1}:{2}'.format(self.id, start, end)

    @djcached(__gen_score_cache_key, 24 * 3600)
    def get_score(self, start=None, end=None):
        metric = Metric.objects.root_nodes()[:1][0]
        return metric.get_result(self, start, end)


class EmailDomain(EmailDomain):
    objects = QuerySetManager()

    class Meta:
        proxy = True

    class QuerySet(models.query.QuerySet):
        def with_commit_count(self):
            return self.values('domain') \
                .annotate(commit_count=models.Count('addresses__owner__'
                                                    'committer_ids__'
                                                    'commits__id',
                                                    distinct=True),
                          address_count=models.Count('addresses__id',
                                                     distinct=True)) \
                .order_by('-commit_count')

        def with_mlpost_count(self):
            return self.values('domain') \
                .annotate(mlpost_count=models.Count('addresses__owner__'
                                                    'mailing_list_'
                                                    'posts__id',
                                                    distinct=True),
                          address_count=models.Count('addresses__id',
                                                     distinct=True)) \
                .order_by('-mlpost_count')

        def with_btcomment_count(self):
            return self.values('domain') \
                .annotate(btcomment_count=models.Count('addresses__owner__'
                                                       'bug_comments__id',
                                                       distinct=True),
                          address_count=models.Count('addresses__id',
                                                     distinct=True)) \
                .order_by('-btcomment_count')

        def with_participant_count(self):
            return self.values('domain') \
                .annotate(participant_count=models.Count('addresses__owner__'
                                                         'id', distinct=True),
                          address_count=models.Count('addresses__id',
                                                     distinct=True)) \
                .order_by('-participant_count')


class MetricScoreConstants(models.Model):
    red_score = models.FloatField()
    yellow_score = models.FloatField()
    green_score = models.FloatField()

    ry_boundary = models.FloatField()
    yg_boundary = models.FloatField()

    class Meta:
        verbose_name = "Metric Score Constants"
        verbose_name_plural = "Metric Score Constants instances"

    def clean(self):
        if not (self.red_score <= self.ry_boundary <= self.yellow_score
                <= self.yg_boundary <= self.green_score):
            raise ValidationError("Green score should be highest, followed by "
                                  "yg boundary, yellow score, ry boundary, "
                                  "and red score")

    def save(self, *args, **kwargs):
        self.clean()

        return super(MetricScoreConstants, self).save(*args, **kwargs)

    def __str__(self):
        return '(red=%.2f, ry=%.2f, yellow=%.2f, yg=%.2f, green=%.2f)' % (
            self.red_score,
            self.ry_boundary,
            self.yellow_score,
            self.yg_boundary,
            self.green_score)


class MetricAlgorithm(models.Model):
    name = models.CharField(max_length=50, unique=True)
    desc = models.CharField(max_length=300)

    objects = get_natural_key_manager('name')

    def __str__(self):
        return self.name


class Metric(MPTTModel):
    parent = TreeForeignKey('self', related_name='children',
                            null=True, blank=True)
    weight = models.IntegerField()
    algorithm = models.ForeignKey(MetricAlgorithm, null=True, blank=True)
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    template_name = models.CharField(max_length=50, blank=True, default='')
    sibling_order = models.IntegerField(default=0, blank=True)
    colour = colorful.fields.RGBColorField(blank=True)

    time_based = models.BooleanField(default=True)

    tree = TreeManager()

    class MPTTMeta:
        ordering = ('tree_id', 'level', 'sibling_order')
        order_insertion_by = ('sibling_order')

    def __str__(self):
        return self.title

    def clean(self):
        if not self.title and self.algorithm is not None:
            self.title = self.algorithm.desc

        # HACK: We currently have no way to blank out the colour, so detect
        # black and blank it out. This requires improvements in django-colorful
        # to fix.
        if self.colour == '#000000':
            self.colour = ''

    def get_result(self, project, start=None, end=None):
        return self.cached_scores.get(project=project, start=start, end=end)


class MetricCache(models.Model):
    project = TreeForeignKey(Project, related_name='cached_scores')
    metric = TreeForeignKey(Metric, related_name='cached_scores')
    raw_value = JSONField(null=True)
    score = models.FloatField()
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    is_complete = models.BooleanField()
    is_dirty = models.BooleanField(default=False)

    objects = QuerySetManager()

    class Meta:
        unique_together = ('project', 'metric', 'start', 'end')

    def __init__(self, *args, **kwargs):
        # Allow children to be injected in
        try:
            self._children = kwargs.pop('children')
        except KeyError:
            pass

        super(MetricCache, self).__init__(*args, **kwargs)

    def update_id(self):
        """
        Set .id so that we update existing entries if a score tree already
        exists.
        """
        # .id is already set, so don't do anything
        if self.id is not None:
            return

        try:
            self.id = type(self).objects.get(project=self.project,
                                             metric=self.metric,
                                             start=self.start,
                                             end=self.end).id
        except type(self).DoesNotExist:
            pass

        except MultipleObjectsReturned:
            logger.warn("Duplicate MetricCache scores found in the database "
                        "matching (%s, %s, %s, %s). "
                        "Picking the first one...",
                        self.project, self.metric, self.start, self.end)

            self.id = type(self).objects.filter(project=self.project,
                                                metric=self.metric,
                                                start=self.start,
                                                end=self.end)[:1][0].id

    def save_all(self):
        """
        Recursively save results into database
        """
        try:
            children = self.children

        except AttributeError:
            children = []

        for child in children:
            child.save_all()

        self.update_id()
        self.save()

    # virtual fields
    @cached_property
    def parent(self):
        try:
            return self._parent
        except AttributeError:
            return self.metric.parent.get_result(project=self.project,
                                                 start=self.start,
                                                 end=self.end)

    @cached_property
    def children(self):
        try:
            return self._children
        except AttributeError:
            qs = type(self).objects \
                           .filter(project=self.project_id,
                                   start=self.start, end=self.end,
                                   metric__in=self.metric.get_children()) \
                           .select_related('metric__algorithm') \
                           .order_by('metric__lft')

            for metric in qs:
                metric._parent = self

            return qs

    @cached_property
    def colour(self):
        return score_to_colour(self.score)

    @cached_property
    def weight(self):
        return self.metric.weight

    @cached_property
    def weight_normalized_score(self):
        return (self.score / 100.0 * self.weight)

    @cached_property
    def normalized_weight(self):
        if self.metric.parent_id is None:
            return 100

        total = sum(m.weight for m in self.parent.children)

        return float(self.metric.weight) / total * 100

    @cached_property
    def leaf_children(self):
        return [child for child in self.children if not child.children]

    @cached_property
    def aggregate_children(self):
        return [child for child in self.children if child.children]

    class QuerySet(models.query.QuerySet):
        def columnwise(self, cols_before=[], cols_after=[]):
            args = cols_before[:]
            args.extend(('metric__tree_id', 'metric__lft', 'metric__id'))
            args.extend(cols_after)

            return self.order_by(*args)

        def iter_by_metric(self, metric_cols, cols, datalist_order=None):
            """
            Helper function to allow for iterating using a nested loop,
            grouped by metric.

            Yields an AttrDict keyed by metric_cols, with a "datalist" key
            containing AttrDict's keyed by cols.

            @param metric_cols List of columns from the Metric table to query
            @param cols List of columns from MetricCache table to query
            @param datalist_order 2-tuple of (key, ordered_value_list)
            """
            # Make sure we select the metric.id column
            metric_cols = set(metric_cols) | set(['id'])

            cols = ['metric__' + i for i in metric_cols] + cols

            metricid = None
            current_metric = None
            current_datalist = {}

            if datalist_order is not None:
                datalist_order_lookup = dict(zip(datalist_order[1],
                                                 itertools.count()))

                def sort_keyfn(data):
                    return datalist_order_lookup[data[datalist_order[0]]]

                def sort_datalist():
                    current_metric.datalist = sorted(current_metric.datalist,
                                                     key=sort_keyfn)
            else:
                def sort_datalist():
                    pass

            for row in self.columnwise(cols_after=cols).values(*cols):
                # new metric
                if row['metric__id'] != metricid:
                    if current_metric is not None:
                        sort_datalist()
                        yield current_metric
                    metricid = row['metric__id']
                    current_metric = AttrDict((k, row['metric__' + k])
                                              for k in metric_cols)
                    current_metric.datalist = []

                # decode raw_value if not null
                current_data = AttrDict((k, row[k]) for k in cols)
                value = current_data.get('raw_value', None)
                if value is not None:
                    current_data['raw_value'] = json.loads(value)

                current_metric.datalist.append(current_data)

            if current_metric is not None:
                sort_datalist()
                yield current_metric

        def get_latest(self):
            return self.filter(end=None).columnwise()


__all__ = [
    'Participant',
    'EmailAddress',
    'EmailDomain',
    'Options',
    'Project',
    'MetricScoreConstants',
    'MetricAlgorithm',
    'Metric',
    'MetricCache',
]
