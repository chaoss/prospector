# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import abc
from functools import wraps
from healthmeter.hmeter_frontend.utils import (cached_property, djcached,
                                               project_cache_key_template)
from ..constants import red_score, yellow_score, green_score


class MetricAlgorithm(object):
    """
    Base class for implementing Metrics
    """
    __metaclass__ = abc.ABCMeta

    def score_project(self, project, start=None, end=None):
        self.project = project
        self.start = start
        self.end = end

        # Pre-evaluate this so that it gets cached
        return self.normalized_score

    @property
    def projects(self):
        return self.project.all_projects

    @property
    def green_score(self):
        return green_score()

    @property
    def yellow_score(self):
        return yellow_score()

    @property
    def red_score(self):
        return red_score()

    @cached_property
    def raw_value(self):
        return self.get_raw_value()

    @abc.abstractproperty
    def normalizer():
        pass

    @cached_property
    def normalized_score(self):
        return self.normalizer(self.raw_value)

    @abc.abstractmethod
    def get_raw_value(self):
        pass

    @classmethod
    def as_metric(cls, *initargs, **initkwargs):
        @wraps(cls)
        def metricfn(project, start=None, end=None):
            metric_inst = cls(*initargs, **initkwargs)
            metric_inst.score_project(project, start, end)
            return metric_inst
        return metricfn

    @property
    @djcached(
        lambda self: project_cache_key_template.format(
            id=self.project.id,
            key=type(self).__name__ + ':is_complete'),
        6 * 3600)
    def is_complete(self):
        return self._is_complete

    @abc.abstractproperty
    def _is_complete(self):
        pass
