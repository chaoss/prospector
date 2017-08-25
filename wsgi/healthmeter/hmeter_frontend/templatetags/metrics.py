# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe
import json

from healthmeter.hmeter_frontend.metrics.lookup import get_metricunit

register = template.Library()


@register.filter
def format_score(value):
    if value is None:
        return "N/A"

    if type(value) is bool:
        return u'\u2714' if value else u'\u2718'

    elif type(value) is int:
        return intcomma(value)

    f = floatformat(value, 2)
    if f:
        return f

    return unicode(value)


@register.filter
def jsonify_score_tree(score, autoescape=None):
    def convert_score(score):
        ret = {'description': score.metric.description,
               'title': score.metric.title,
               'score': score.score,
               'weight': score.normalized_weight,
               'metric_id': score.metric.id,
               'children': [convert_score(child) for child in score.children]}

        if score.metric.colour:
            ret['colour'] = score.metric.colour

        return ret

    return mark_safe(json.dumps(convert_score(score)))


@register.filter
def metric_unit(metric_result):
    return get_metricunit(metric_result.metric.algorithm.name,
                          metric_result.raw_value)
