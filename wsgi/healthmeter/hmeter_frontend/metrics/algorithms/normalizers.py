# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import abc
from healthmeter.hmeter_frontend.utils.cache import cached_property
from ..constants import red_score, yellow_score, green_score


class Normalizer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, value):
        """
        Normalizes a value into a metric score.

        @arg value Raw value to normalize into a score
        """
        pass


class ClampingNormalizer(Normalizer):
    """
    Clamp a continuous value into green, red, or yellow, by fitting it into the
    ranges between green_threshold and yellow_threshold.
    """
    def __init__(self, green_threshold, yellow_threshold):
        self.green_threshold = green_threshold
        self.yellow_threshold = yellow_threshold
        self.thresholds = sorted([green_threshold, yellow_threshold])

    # calculate this lazily to avoid querying the database unnecessarily.
    @cached_property
    def scores(self):
        if self.yellow_threshold == self.thresholds[0]:
            # normal operation:
            # -------- value ------>
            # red -> yellow -> green
            return [red_score(), yellow_score(), green_score()]

        else:
            # reverse operation:
            # -------- value ------>
            # green -> yellow -> red
            return [green_score(), yellow_score(), red_score()]

    def __call__(self, value):
        if value is None:
            return red_score()

        idx = 0
        for t in self.thresholds:
            if value < t:
                return self.scores[idx]

            idx += 1

        return self.scores[idx]


class DemographicNormalizer(ClampingNormalizer):
    def __init__(self):
        super(DemographicNormalizer, self).__init__(green_threshold=35.0,
                                                    yellow_threshold=50.0)


class UniqueDomainsNormalizer(ClampingNormalizer):
    def __init__(self):
        super(UniqueDomainsNormalizer, self).__init__(green_threshold=5,
                                                      yellow_threshold=2)


class BoolNormalizer(Normalizer):
    """
    Normalizer that returns green when True, red otherwise
    """
    def __call__(self, value):
        return green_score() if value else red_score()


class StaticNormalizer(Normalizer):
    """
    Normalizer that returns a fixed score

    @arg score Static score to return. May be callable for lazy-evaluation.
    """
    def __init__(self, score):
        self.score = score

    def __call__(self, value):
        if callable(self.score):
            return self.score()
        else:
            return self.score
