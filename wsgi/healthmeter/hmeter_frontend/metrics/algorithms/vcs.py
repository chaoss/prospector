# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import healthmeter.participantinfo.models as participantmodels
import healthmeter.vcsinfo.models as vcsmodels

from ... import models

from ..lookup import metric
from .mixins import (LastUpdatedChecker, DomainMetric,
                     PercentageMetric, TimeBasedMetric)
from .normalizers import (ClampingNormalizer, DemographicNormalizer,
                          UniqueDomainsNormalizer)


class VCSMetric(LastUpdatedChecker, TimeBasedMetric):
    @property
    def repositories(self):
        return vcsmodels.Repository.objects.filter(project__in=self.projects)

    queryset = repositories

    @property
    def commits(self):
        qs = vcsmodels.Commit.objects.filter(repository__in=self.repositories)
        return self.clamp_timestamp(qs, 'timestamp')


@metric
class CommitterDemographic(PercentageMetric, VCSMetric):
    normalizer = DemographicNormalizer()

    @property
    def participants(self):
        return participantmodels.Participant.objects \
            .filter(committer_ids__commits__in=self.commits) \
            .distinct('pk')

    def get_denominator(self):
        return self.participants.count()

    def get_numerator(self):
        try:
            return models.EmailDomain.objects \
                .filter(addresses__owner__in=self.participants) \
                .with_participant_count()[:1][0]['participant_count']

        except IndexError:
            return None


@metric
class CommitterUniqueDomains(DomainMetric, VCSMetric):
    def get_raw_value(self):
        if not self.repositories.exists():
            return None

        return self.commits \
            .values('author__participant__email_addresses__domainpart_id') \
            .distinct() \
            .count()


@metric
class CommitRatio(PercentageMetric, VCSMetric):
    normalizer = DemographicNormalizer()

    def get_denominator(self):
        return self.commits.count()

    def get_numerator(self):
        try:
            return models.EmailDomain.objects \
                .filter(addresses__owner__committer_ids__commits__in=(
                    self.commits)) \
                .with_commit_count()[:1][0]['commit_count']

        except IndexError:
            return None


@metric
class CommitRatioByParticipant(PercentageMetric, VCSMetric):
    normalizer = DemographicNormalizer()

    def get_denominator(self):
        return self.commits.count()

    def get_numerator(self):
        if not self.repositories.exists():
            return None

        try:
            return self.commits \
                       .values('author') \
                       .annotate(commit_count=Count('id')) \
                       .order_by('-commit_count')[:1][0]['commit_count']

        except IndexError:
            return None


@metric
class CommitterCount(VCSMetric):
    normalizer = ClampingNormalizer(green_threshold=3, yellow_threshold=2)

    unit = 'committer'

    def get_raw_value(self):
        if not self.repositories.exists():
            return None

        return self.commits.values('author').distinct().count()
