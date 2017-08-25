# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.db.models import Min, Max
from healthmeter.hmeter_frontend import models
from healthmeter.bloginfo import models as blogmodels
from healthmeter.hmeter_frontend.utils.iterators import intervals

from ..lookup import metric
from .mixins import (FrequencyMetric, LastUpdatedChecker, TimeBasedMetric,
                     UnimplementedMetric)
from .normalizers import ClampingNormalizer


# Blog metrics
class BlogMetric(LastUpdatedChecker, TimeBasedMetric):
    @property
    def posts(self):
        qs = blogmodels.Post.objects.filter(blog__projects__in=self.projects) \
                                    .order_by('timestamp')
        return self.clamp_timestamp(qs, 'timestamp')

    @property
    def blogs(self):
        return self.project.all_blogs

    queryset = blogs

    @property
    def post_intervals(self):
        timestamps = (post.timestamp for post in self.posts)
        return (interval.days for interval in intervals(timestamps))


@metric
class BlogPostFrequency(FrequencyMetric, BlogMetric):
    normalizer = ClampingNormalizer(green_threshold=5, yellow_threshold=2)

    unit = 'blog post per month'
    unit_plural = 'blog posts per month'

    def get_quantity(self):
        return self.posts.count()

    def get_period(self):
        dates = self.posts.aggregate(first=Min('timestamp'),
                                     last=Max('timestamp'))

        return ((dates['last'] - dates['first']).days /
                30.0)


@metric
class BlogPostMinInterval(BlogMetric):
    normalizer = ClampingNormalizer(green_threshold=10, yellow_threshold=6)

    unit = 'day'

    def get_raw_value(self):
        try:
            return min(self.post_intervals)
        except ValueError:
            return None


@metric
class BlogPostMaxInterval(BlogMetric):
    normalizer = ClampingNormalizer(green_threshold=10, yellow_threshold=6)

    unit = 'day'

    def get_raw_value(self):
        try:
            return max(self.post_intervals)
        except ValueError:
            return None


# Publicity metrics
@metric
class DownloadFrequency(UnimplementedMetric):
    pass


@metric
class DownloadFrequency(UnimplementedMetric):
    pass


@metric
class GoogleTrendsIsUpwards(UnimplementedMetric):
    pass
