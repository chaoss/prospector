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
        return 0


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
