# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import healthmeter.projectinfo.models as projectmodels
import datetime

from ..lookup import metric
from .base import MetricAlgorithm
from .mixins import NullChecker, TimeBasedMetric
from .normalizers import ClampingNormalizer


@metric
class TimeSinceLastSeenRelease(NullChecker, TimeBasedMetric, MetricAlgorithm):
    normalizer = ClampingNormalizer(green_threshold=6 * 30,
                                    yellow_threshold=12 * 30)

    unit = 'day'

    def get_raw_value(self):
        try:
            releases = self.clamp_timestamp(self.project.all_releases, 'date')
            latest = releases.latest('date').date

        except projectmodels.Release.DoesNotExist:
            return None

        end = (self.end.date() if self.end is not None
               else datetime.date.today())

        return (end - latest).days
