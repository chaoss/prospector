# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import healthmeter.mlinfo.models as mlmodels
from healthmeter.hmeter_frontend import models

from ..lookup import metric
from .mixins import (TimeBasedMetric, LastUpdatedChecker, DomainMetric,
                     PercentageMetric)
from .normalizers import DemographicNormalizer, UniqueDomainsNormalizer


class MailingListMetric(LastUpdatedChecker, TimeBasedMetric):
    @property
    def mailing_lists(self):
        return mlmodels.MailingList.objects \
            .filter(projects__in=self.projects)

    queryset = mailing_lists

    @property
    def posts(self):
        qs = mlmodels.Post.objects \
                          .filter(mailing_lists__in=self.mailing_lists)

        return self.clamp_timestamp(qs, 'timestamp')


@metric
class MailingListPostRatio(PercentageMetric, MailingListMetric):
    normalizer = DemographicNormalizer()

    def get_denominator(self):
        return self.posts.count()

    def get_numerator(self):
        try:
            return models.EmailDomain.objects \
                .filter(addresses__owner__mailing_list_posts__in=self.posts) \
                .with_mlpost_count()[:1][0]['mlpost_count']

        except IndexError:
            return None


@metric
class MailingListPostRatioByParticipant(PercentageMetric, MailingListMetric):
    normalizer = DemographicNormalizer()

    def get_denominator(self):
        return self.posts.count()

    def get_numerator(self):
        try:
            return self.posts.values('author') \
                             .annotate(mlpost_count=Count('id')) \
                             .order_by('-mlpost_count')[:1][0]['mlpost_count']
        except IndexError:
            return None


@metric
class MailingListUniqueDomains(DomainMetric, MailingListMetric):
    def get_raw_value(self):
        if not self.mailing_lists.exists():
            return None

        return self.posts.values('author__email_addresses__domainpart_id') \
            .distinct() \
            .count()


@metric
class MailingListThreadRatio(PercentageMetric, MailingListMetric):
    normalizer = DemographicNormalizer()

    @property
    def threads(self):
        return self.posts.filter(references__isnull=True)

    def get_denominator(self):
        return self.threads.count()

    def get_numerator(self):
        try:
            return models.EmailDomain.objects \
                .filter(addresses__owner__mailing_list_posts__in=(
                    self.threads)) \
                .with_mlpost_count()[:1][0]['mlpost_count']

        except IndexError:
            return None
