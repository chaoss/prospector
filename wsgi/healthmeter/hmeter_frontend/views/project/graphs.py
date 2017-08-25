# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from calendar import timegm
import collections
import contextlib
from datetime import datetime, time, timedelta
import simplejson

from django.db.models import Count
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page

from preferences import preferences

from healthmeter.hmeter_frontend import models

from healthmeter.btinfo import models as btmodels
from healthmeter.bloginfo import models as blogmodels
from healthmeter.eventinfo import models as eventmodels
from healthmeter.gtrendsinfo import models as gtrendsmodels
from healthmeter.ircinfo import models as ircmodels
from healthmeter.jamiqinfo import models as jamiqmodels
from healthmeter.microbloginfo import models as microblogmodels
from healthmeter.mlinfo import models as mlmodels
from healthmeter.projectinfo import models as projectmodels
from healthmeter.vcsinfo import models as vcsmodels

from healthmeter.views.generic import JsonView
from healthmeter.hmeter_frontend.utils.cache import cached_property


class GraphDataView(JsonView):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphDataView, cls).as_view(*args, **kwargs)
        return cache_page(6 * 60 * 60)(view)

    def get(self, request, id, *args, **kwargs):
        self.project = models.Project.objects.get(id=id)
        self.projects = self.project.all_projects

        return super(GraphDataView, self).get(request, *args, **kwargs)

    def get_data(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(GraphDataView, self).get_context_data(**kwargs)
        context['data'] = self.get_data()
        return context

    @staticmethod
    def get_datestamp(d):
        """Return the Flot datestamp for a datetime.date object"""
        return timegm(datetime.combine(d, time()).timetuple()) * 1000


class FrequencyDataView(GraphDataView):
    series_name = None
    timestamp_column = 'timestamp'
    count_column = 'pk'
    queryset = None
    querysets = {}

    def get_queryset(self):
        return self.queryset

    def get_querysets(self):
        if self.series_name:
            if self.querysets:
                raise ImproperlyConfigured("series_name cannot be set when "
                                           "querysets is also set.")

            return ((self.series_name,
                    self.get_queryset(),
                    self.timestamp_column),)

        else:
            return self.querysets

    @classmethod
    def gen_freq_series(cls, qs, timestamp_column):
        """
        Get frequency data series for Flot from `series'

        @arg series series with timestamp column for generating data series
        from @arg timestamp_column Name of timestamp column

        @return Frequency data in the format [[timestamp, freq], ...]
        """

        qs = qs.extra(select={'datestamp': ('date({0})'
                                            .format(timestamp_column))}) \
            .values('datestamp') \
            .annotate(count=Count(cls.count_column, distinct=True)) \
            .order_by('datestamp')

        def seriesgenerator():
            prev_date = None
            for i in qs:
                current_date = i['datestamp']

                if prev_date is not None:
                    for j in xrange(1, (current_date - prev_date).days):
                        yield [cls.get_datestamp(prev_date + timedelta(j)), 0]

                prev_date = current_date

                yield [cls.get_datestamp(current_date), i['count']]

        return list(seriesgenerator())

    def get_data(self):
        querysets = self.get_querysets()
        data = {}

        for series_name, qs, timestamp_column in querysets:
            data[series_name] = self.gen_freq_series(qs, timestamp_column)

        if len(data) == 1:
            return data.values()[0]

        return data


class ContributorDataView(FrequencyDataView):
    """
    Abstract view for contributors vs time graphs
    """
    count_column = 'author'


class DomainFilterMixin(object):
    def filter_by_domain(self, qs):
        domain = self.kwargs.get('domain')

        if not domain:
            return qs

        return qs.filter(**{self.domain_rel_kw: domain})


class CommitDataView(FrequencyDataView, DomainFilterMixin):
    series_name = 'commit_per_day_series'
    domain_rel_kw = 'author__participant__email_addresses__domainpart__domain'

    def get_queryset(self):
        qs = vcsmodels.Commit.objects \
            .filter(repository__project__in=self.projects) \
            .distinct()

        return self.filter_by_domain(qs)


class CommitterDataView(CommitDataView, ContributorDataView):
    series_name = 'committer_per_day_series'


class MailingListDataView(FrequencyDataView, DomainFilterMixin):
    series_name = 'email_per_day_series'
    domain_rel_kw = 'author__email_addresses__domainpart__domain'

    def get_queryset(self):
        qs = mlmodels.Post.objects \
            .filter(mailing_lists__projects__in=self.projects) \
            .distinct()

        return self.filter_by_domain(qs)


class MailingListPosterDataView(MailingListDataView, ContributorDataView):
    series_name = 'ml_poster_per_day_series'


class BugDataView(FrequencyDataView, DomainFilterMixin):
    domain_rel_kw = 'author__email_addresses__domainpart__domain'

    def get_querysets(self):
        bt_infos = btmodels.BugNamespace.objects \
            .filter(projects__in=self.projects) \
            .distinct()
        bugs = btmodels.Bug.objects.filter(tracker_info__in=bt_infos)

        # closed bugs series
        bugs_closed = bugs.exclude(close_date=None)

        # first comment == bug opening comment
        firstcomments = btmodels.Comment.objects \
            .filter(bug__tracker_info__in=bt_infos) \
            .distinct('bug')
        # Wrap around using IN operator because Django doesn't know how to use
        # annotate with distinct
        firstcomments = btmodels.Comment.objects \
            .filter(id__in=firstcomments)

        firstcomments = self.filter_by_domain(firstcomments)
        bugs_closed = bugs_closed.filter(
            id__in=firstcomments.values('bug_id'))

        return (('bugs_opened_series', firstcomments, 'timestamp'),
                ('bugs_closed_series', bugs_closed, 'close_date'))


class BugReporterDataView(ContributorDataView, DomainFilterMixin):
    count_column = 'author'
    series_name = 'bug_reporters_per_day_series'
    domain_rel_kw = 'author__email_addresses__domainpart__domain'

    def get_queryset(self):
        return self.filter_by_domain(btmodels.Comment.objects.filter(
            bug__tracker_info__projects__in=self.projects))


class IrcDataView(GraphDataView):
    def get_data(self):
        meetings = ircmodels.Meeting.objects \
            .filter(channel__projects__in=self.projects)
        meetings = meetings.with_msg_count().with_participant_count()

        data = {}
        data['irc_lines_per_meeting_series'] = [
            [self.get_datestamp(x.time_start), int(x.msg_count)]
            for x in meetings]

        data['irc_logins_per_meeting_series'] = [
            [self.get_datestamp(x.time_start), int(x.participant_count)]
            for x in meetings]

        return data


class BlogDataView(FrequencyDataView):
    series_name = 'blogposts_per_day_series'

    def get_queryset(self):
        return blogmodels.Post.objects.filter(blog__projects__in=self.projects)


class MicroblogDataView(FrequencyDataView):
    series_name = 'microblogposts_per_day_series'

    def get_queryset(self):
        return microblogmodels.MicroblogPost.objects.filter(
            microblog__projects__in=self.projects)


class EventDataView(GraphDataView):
    def get_data(self):
        releases = projectmodels.Release.objects.filter(
            project__in=self.projects)
        inf = float("inf")
        data = {}
        data['release_series'] = [
            [[self.get_datestamp(release.date), "-Infinity"],
             [self.get_datestamp(release.date), "Infinity"]]
            for release in releases]
        data['release_labels'] = [release.version for release in releases]

        events = eventmodels.Event.objects.filter(project__in=self.projects)
        data['event_series'] = [
            [[self.get_datestamp(event.date_start), "-Infinity"],
             [self.get_datestamp(event.date_end), "Infinity"]]
            for event in events]
        data['event_labels'] = [event.desc for event in events]

        meetings = ircmodels.Meeting.objects \
            .filter(channel__projects__in=self.projects)
        data['meeting_series'] = [
            [[self.get_datestamp(meeting.time_start.date()), "-Infinity"],
             [self.get_datestamp(meeting.time_end.date()), "Infinity"]]
            for meeting in meetings]

        blog_posts = blogmodels.Post.objects \
            .filter(blog__projects__in=self.projects)
        data['blog_series'] = [
            [[self.get_datestamp(blog_post.timestamp.date()), "-Infinity"],
             [self.get_datestamp(blog_post.timestamp.date()), "Infinity"]]
            for blog_post in blog_posts]

        data['blog_labels'] = [blog_post.title for blog_post in blog_posts]

        return data


class GTrendsDataView(GraphDataView):
    @property
    def all_trends(self):
        return gtrendsmodels.Query.objects.filter(project__in=self.projects)

    def get_data(self):
        series = []
        for trend in self.all_trends:
            keyword = trend.keyword
            datapoints = [(self.get_datestamp(d.start),
                           d.count) for d in trend.datapoints.all()]

            series.append({'label': keyword,
                           'series': datapoints})

        return series


class JamiqDataView(GraphDataView):
    @property
    def datapoints(self):
        return jamiqmodels.DataPoint \
            .objects \
            .filter(topic__projects__in=self.projects) \
            .aggregate_by_date() \
            .order_by('datestamp')

    def make_series(self, datapoints, attr):
        result = []

        for dp in datapoints:
            value = dp[attr]
            datestamp = dp['datestamp']

            result.append((self.get_datestamp(datestamp), value))

        return result

    def get_data(self):
        datapoints = self.datapoints
        series = {}

        for i in ('positive', 'neutral', 'negative'):
            series[i] = self.make_series(datapoints, i)

        return series


class MetricDataView(GraphDataView):
    @cached_property
    def max_level(self):
        try:
            return int(self.request.GET['maxlevel'])
        except KeyError:
            return None

    @cached_property
    def metrics(self):
        filter_args = {}
        if self.max_level is not None:
            filter_args['level__lte'] = self.max_level

        return models.Metric.objects.root_nodes() \
                                    .get() \
                                    .get_descendants(include_self=True) \
                                    .filter(**filter_args)

    def get_legend(self):
        return dict(
            (metric.id, {'id': metric.id,
                         'title': metric.title,
                         'time_based': metric.time_based,
                         'colour': metric.colour,
                         'weight': metric.weight})
            for metric in self.metrics)

    def get_metricseries(self):
        qs = self.project.cached_scores.filter(metric__in=self.metrics,
                                               end__isnull=False) \
                                       .order_by('metric__id', 'end') \
                                       .values_list('metric_id',
                                                    'metric__time_based',
                                                    'end', 'score')

        series = collections.defaultdict(collections.deque)
        for metricid, timebased, dt, score in qs.iterator():
            if timebased:
                series[metricid].append([self.get_datestamp(dt.date()), score])
            else:
                series[metricid] = score

        for k in series.keys():
            try:
                series[k] = list(series[k])
            except TypeError:
                pass            # Sometimes non-iterable if timebased=True

        return series

    def get_tree(self):
        stack = []

        for metric in self.metrics:
            node = {'id': metric.id, 'children': []}
            level = metric.level
            try:
                stack[level] = node
            except IndexError:
                stack.append(node)
                assert(level + 1 == len(stack))

            if level > 0:
                stack[level - 1]['children'].append(node)

        return stack[0]

    def get_data(self):
        return {
            'legend': self.get_legend(),
            'metric_series': self.get_metricseries(),
            'tree': self.get_tree(),
            'kwargs': self.kwargs
        }
