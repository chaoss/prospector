# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db.models import Sum
import itertools
from healthmeter.hmeter_frontend import models
import healthmeter.vcsinfo.models as vcsmodels


from ..lookup import metric
from .mixins import RatioMetric
from .normalizers import ClampingNormalizer
from .vcs import VCSMetric
from .bugs import BugReportMetric


class SlocMetric(VCSMetric):
    @property
    def sloc(self):
        main_branches = self.branches.filter(is_main=True)
        head_commits = vcsmodels.Commit.objects \
                                       .filter(branches__in=main_branches)

        sloc = 0

        for commit in head_commits:
            try:
                commit_ids = itertools.chain(
                    (c.id for c in commit.get_ancestors()),
                    [commit.id])
                commits = vcsmodels.Commit.objects.filter(id__in=commit_ids)

                if self.end:
                    commits = commits.filter(timestamp__lte=self.end)

                latest = commits.latest('timestamp')
            except vcsmodels.Commit.DoesNotExist:
                latest = commit

            sloc += latest.line_count

        return sloc


@metric
class BugsPerKLOC(RatioMetric, BugReportMetric, SlocMetric):
    normalizer = ClampingNormalizer(green_threshold=5.0, yellow_threshold=10.0)

    unit = 'bug per KLOC'
    unit_plural = 'bugs per KLOC'

    def get_denominator(self):
        sloc = self.sloc

        return sloc if sloc is not None else None

    def get_numerator(self):
        if not self.bugnamespaces.exists():
            return None

        return self.first_comments.count()


@metric
class BugsClosedRatio(RatioMetric, BugReportMetric):
    normalizer = ClampingNormalizer(green_threshold=1.0, yellow_threshold=2.0)

    def get_denominator(self):
        return self.first_comments.count()

    def get_numerator(self):
        return self.first_comments.filter(bug__close_date__isnull=False) \
                                  .count()
