# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from healthmeter.hmeter_frontend.utils.iterators import intervals
from healthmeter.eventinfo import models as eventmodels
from ..lookup import metric

from .mixins import FrequencyMetric, NullChecker, TimeBasedMetric
from .normalizers import ClampingNormalizer


class EventMetric(NullChecker, TimeBasedMetric):
    @property
    def events(self):
        qs = eventmodels.Event.objects.filter(project__in=self.projects) \
                                      .order_by('date_start')
        return self.clamp_timestamp(qs, 'date_start')

    @property
    def event_intervals(self):
        timestamps = (x.date_start for x in self.events)
        return (x.days for x in intervals(timestamps))


@metric
class EventFrequency(FrequencyMetric, EventMetric):
    normalizer = ClampingNormalizer(green_threshold=2,
                                    yellow_threshold=1)

    unit = 'event per month'
    unit_plural = 'events per month'

    def get_quantity(self):
        return self.events.count()

    def get_period(self):
        first_date = self.events[0].date_start
        last_date = self.end.date() if self.end else datetime.date.today()
        return (last_date - first_date).days / 30.0


@metric
class EventMaxInterval(EventMetric):
    normalizer = ClampingNormalizer(green_threshold=2, yellow_threshold=1)

    unit = 'day'

    def get_raw_value(self):
        try:
            return max(x / 30.0 for x in self.event_intervals)
        except ValueError:
            return None
