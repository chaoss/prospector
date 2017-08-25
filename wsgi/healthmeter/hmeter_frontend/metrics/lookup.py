# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from collections import namedtuple

registered_algorithms = {}
MetricAlgoEntry = namedtuple('MetricAlgoEntry', ['fn', 'cls'])


def metric(cls):
    global registered_algorithms
    registered_algorithms[cls.__name__] = MetricAlgoEntry(cls.as_metric(), cls)
    return cls


def get_metricalgo(metricname):
    return registered_algorithms[metricname].fn


def get_metriccls(metricname):
    return registered_algorithms[metricname].cls


def get_metricunit(metricname, value):
    if value is None:
        return ''

    cls = get_metriccls(metricname)

    unit = getattr(cls, 'unit', None)

    # Check for plural
    if value != 1 and unit is not None:
        unit = getattr(cls, 'unit_plural', unit + 's')

    # Set to empty string if no unit
    if unit is None:
        unit = ''

    # Prepend space to unit unless percentage
    return ' ' + unit if unit and unit != '%' else unit
