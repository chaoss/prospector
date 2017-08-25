# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from healthmeter.hmeter_frontend.utils.cache import cached_property
from healthmeter.hmeter_frontend import models
import healthmeter.ircinfo.models as ircmodels
from ..lookup import metric

from .base import MetricAlgorithm
from .mixins import (FrequencyMetric, LastUpdatedChecker, RatioMetric,
                     TimeBasedMetric)
from .normalizers import ClampingNormalizer


class IrcMetric(LastUpdatedChecker, TimeBasedMetric):
    @property
    def channels(self):
        return ircmodels.Channel.objects \
            .filter(projects__in=self.projects)

    queryset = channels

    @property
    def _is_complete(self):
        return not self.queryset.filter(last_updated=None) \
                                .exclude(meeting_logs_url=None).exists()

    @property
    def meetings(self):
        qs = ircmodels.Meeting.objects.filter(channel__in=self.channels)
        return self.clamp_timestamp(qs, 'time_start')

    @property
    def messages(self):
        qs = ircmodels.Message.objects.filter(channel__in=self.channels)
        return self.clamp_timestamp(qs, 'timestamp')


# IRC metrics
@metric
class IrcChannelsNumber(IrcMetric):
    normalizer = ClampingNormalizer(green_threshold=2, yellow_threshold=1)

    unit = 'channel'

    def get_raw_value(self):
        return self.channels.count() or None


@metric
class IrcMeetingFrequency(FrequencyMetric, IrcMetric):
    normalizer = ClampingNormalizer(green_threshold=4, yellow_threshold=2)
    unit = 'meeting per month'
    unit_plural = 'meetings per month'

    def get_quantity(self):
        return self.meetings.count()

    def get_period(self):
        first_meeting_time = self.meetings \
                                 .order_by('time_start') \
                                 .values_list('time_start', flat=True)[:1][0]
        end_time = self.end or datetime.datetime.utcnow()

        return (end_time - first_meeting_time).days / 30.0


@metric
class IrcMeetingAverageLines(RatioMetric, IrcMetric):
    normalizer = ClampingNormalizer(green_threshold=10, yellow_threshold=3)
    unit = 'line'

    def get_denominator(self):
        return self.meetings.count()

    def get_numerator(self):
        return self.messages.count()


@metric
class IrcMeetingAverageParticipants(RatioMetric, IrcMetric):
    normalizer = ClampingNormalizer(green_threshold=5, yellow_threshold=2)
    green_threshold = 5
    yellow_threshold = 2

    unit = 'participant'

    @cached_property
    def meetings_list(self):
        meetings = self.meetings \
            .with_participant_count()
        return list(meetings)

    def get_denominator(self):
        return len(self.meetings_list)

    def get_numerator(self):
        return sum(m.participant_count for m in self.meetings_list)
