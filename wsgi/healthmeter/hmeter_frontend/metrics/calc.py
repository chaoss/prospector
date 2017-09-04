# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import healthmeter.hmeter_frontend.metrics.algorithms
from healthmeter.hmeter_frontend.models import MetricCache
from .lookup import get_metricalgo


def calc_score(project, metric, start=None, end=None):
    """
    Applies the metric tree in `metric_tree` to `project` to derive a score
    tree.

    :param project: Project to apply metric tree to
    :param metric_tree: Root Metric object to compute scores for
    """

    if metric.algorithm is None:  # no algo, fall back on weighted average
        children = [calc_score(project, child, start, end)
                    for child in metric.get_children()]

        numerator = sum((result.weight * result.score)
                        for result in children)
        denominator = sum(result.weight for result in children)
        score = float(numerator) / denominator if denominator else None
        raw_value = None
        is_complete = all(child.is_complete for child in children)

    else:
        children = []
        algo = get_metricalgo(metric.algorithm.name)(project, start, end)
        score = algo.normalized_score
        raw_value = algo.raw_value
        is_complete = algo.is_complete

    return MetricCache(project=project,
                       metric=metric,
                       raw_value=raw_value,
                       score=score,
                       start=start,
                       end=end,
                       is_complete=is_complete,
                       children=children)
