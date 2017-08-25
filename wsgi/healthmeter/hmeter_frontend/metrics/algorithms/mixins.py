# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import abc
from healthmeter.hmeter_frontend.utils.cache import cached_property
from .base import MetricAlgorithm
from .normalizers import red_score, StaticNormalizer, UniqueDomainsNormalizer


class NullChecker(object):
    @property
    def _is_complete(self):
        return True


class LastUpdatedChecker(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def queryset(self):
        pass

    @property
    def _is_complete(self):
        return not self.queryset.filter(last_updated=None).exists()


class TimeBasedMetric(MetricAlgorithm):
    def clamp_timestamp(self, qs, timestamp_col):
        kwargs = {}
        if self.start:
            kwargs['{0}__gte'.format(timestamp_col)] = self.start

        if self.end:
            kwargs['{0}__lte'.format(timestamp_col)] = self.end

        return qs.filter(**kwargs)


class RatioMetric(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_denominator(self):
        pass

    @abc.abstractmethod
    def get_numerator(self):
        pass

    @cached_property
    def denominator(self):
        return self.get_denominator()

    @cached_property
    def numerator(self):
        return self.get_numerator()

    def has_ratio(self):
        # This checks that denominator is not zero or None, and that numerator
        # is not None, in that order. This is relevant for most ratios.
        return (self.denominator and self.numerator is not None)

    def get_raw_value(self):
        if not self.has_ratio():
            return None

        return float(self.numerator) / self.denominator


class PercentageMetric(RatioMetric):
    unit = '%'
    unit_plural = '%'

    def get_raw_value(self):
        ret = super(PercentageMetric, self).get_raw_value()
        return None if ret is None else ret * 100


class FrequencyMetric(RatioMetric):
    def has_ratio(self):
        # Reverse the order of checking -- since this is a frequency, we can't
        # find the period if quantity is 0.
        return (self.numerator and self.denominator)

    def get_denominator(self):
        return self.get_period()

    def get_numerator(self):
        return self.get_quantity()


class DomainMetric(object):
    unit = 'domain'
    normalizer = UniqueDomainsNormalizer()


class UnimplementedMetric(NullChecker, MetricAlgorithm):
    normalizer = StaticNormalizer(red_score)

    def get_raw_value(self):
        return None
