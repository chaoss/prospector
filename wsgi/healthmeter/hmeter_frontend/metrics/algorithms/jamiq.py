# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
import itertools

import healthmeter.jamiqinfo.models as jamiqmodels

from ..lookup import metric
from .mixins import LastUpdatedChecker, TimeBasedMetric
from .normalizers import ClampingNormalizer


# JamiQ metrics
class JamiqMetric(LastUpdatedChecker, TimeBasedMetric):
    @property
    def topics(self):
        return self.project.all_jamiqtopics

    queryset = topics

    @property
    def datapoints(self):
        """
        Returns JamiQ datapoints `self.projects' sorted in
        reverse-chronological order.
        """
        qs = jamiqmodels.DataPoint.objects.filter(topic__in=self.topics) \
                                          .aggregate_by_date() \
                                          .order_by('-datestamp')
        return self.clamp_timestamp(qs, 'datestamp')

    @property
    def ppi_series(self):
        """
        Iterator that gets the Post Positivity Index series in reverse
        chronological order. The values are calculated by getting the
        difference between the number of positive posts compared to the
        negative posts, and divided by total number of posts.
        """
        for i in self.datapoints.iterator():
            total_posts = i['positive'] + i['negative'] + i['neutral']
            pdiff = i['positive'] - i['negative']

            if total_posts:
                yield float(pdiff) / total_posts

            else:
                yield 0.0

    filter_window = 7

    @property
    def smoothened_ppi_series(self):
        """
        self.ppi_series smoothened using a moving average filter with window
        size `self.filter_window'
        """
        current_sum = 0
        queue = collections.deque([], self.filter_window)

        for i in self.ppi_series:
            if len(queue) == self.filter_window:
                current_sum -= queue.popleft()

            queue.append(i)
            current_sum += i

            if len(queue) == self.filter_window:
                yield current_sum / self.filter_window


@metric
class JamiqPositivePostsTrend(JamiqMetric):
    normalizer = ClampingNormalizer(green_threshold=0.1, yellow_threshold=-0.1)

    def get_raw_value(self):
        points = tuple(itertools.islice(self.smoothened_ppi_series, 2))

        try:
            return points[0] - points[-1]

        except IndexError:
            return None


@metric
class JamiqAveragePostSentiment(JamiqMetric):
    normalizer = ClampingNormalizer(green_threshold=0.1, yellow_threshold=-0.1)

    def get_raw_value(self):
        try:
            return tuple(itertools.islice(self.smoothened_ppi_series, 1))[0]

        except IndexError:
            return None
