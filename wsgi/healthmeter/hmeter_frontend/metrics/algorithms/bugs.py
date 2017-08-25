# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db.models import Count

from healthmeter.participantinfo import models as participantmodels
from healthmeter.btinfo import models as btmodels

from ... import models
from ..lookup import metric

from .base import MetricAlgorithm
from .mixins import (LastUpdatedChecker, DomainMetric,
                     PercentageMetric, TimeBasedMetric)
from .normalizers import DemographicNormalizer, UniqueDomainsNormalizer


class BugReportMetric(LastUpdatedChecker, TimeBasedMetric):
    @property
    def bugnamespaces(self):
        return btmodels.BugNamespace.objects \
            .filter(projects__in=self.projects)

    queryset = bugnamespaces

    @property
    def bugs(self):
        return btmodels.Bug.objects.filter(tracker_info__in=self.bugnamespaces)

    @property
    def comments(self):
        qs = btmodels.Comment.objects.filter(bug__in=self.bugs)
        return self.clamp_timestamp(qs, 'timestamp')

    @property
    def first_comments(self):
        return self.comments \
            .distinct('bug') \
            .order_by('bug', 'timestamp')


@metric
class BugReporterDemographic(PercentageMetric, BugReportMetric):
    normalizer = DemographicNormalizer()

    @property
    def bug_reporters(self):
        return participantmodels.Participant.objects \
            .filter(bug_comments__in=self.first_comments)

    def get_denominator(self):
        return self.bug_reporters.distinct('id').count()

    def get_numerator(self):
        try:
            return participantmodels.EmailAddress.objects \
                .filter(owner__in=self.bug_reporters) \
                .values('domainpart') \
                .annotate(count=Count('owner')) \
                .order_by('-count')[:1][0]['count']

        except IndexError:
            return None


@metric
class BugReportUniqueDomains(DomainMetric, BugReportMetric):
    normalizer = UniqueDomainsNormalizer()

    def get_raw_value(self):
        if not self.bugnamespaces.exists():
            return None

        return self.comments \
            .values('author__email_addresses__domainpart_id') \
            .distinct() \
            .count()


@metric
class BugReportDomainRatio(PercentageMetric, BugReportMetric):
    normalizer = DemographicNormalizer()

    def get_denominator(self):
        return self.first_comments.count()

    def get_numerator(self):
        try:
            return models.EmailDomain.objects \
                .filter(addresses__owner__bug_comments__in=(
                    self.first_comments)) \
                .with_btcomment_count()[:1][0]['btcomment_count']

        except IndexError:
            return None


@metric
class BugReporterRatio(PercentageMetric, BugReportMetric):
    normalizer = DemographicNormalizer()

    def get_denominator(self):
        return self.first_comments.count()

    def get_numerator(self):
        try:
            return btmodels.Comment.objects \
                .filter(id__in=self.first_comments) \
                .values('author', 'bug') \
                .annotate(btcomment_count=Count('id')) \
                .order_by('-btcomment_count')[:1][0]['btcomment_count']

        except IndexError:
            return None
