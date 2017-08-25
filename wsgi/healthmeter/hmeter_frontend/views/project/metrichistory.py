# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
from django.http import Http404
from django.views.generic import DetailView
from healthmeter.hmeter_frontend.models import Project, MetricCache, Metric


MetricData = collections.namedtuple('MetricData', ['value', 'score'])
MetricLine = collections.namedtuple('MetricLine',
                                    ['title', 'level', 'datalist'])


class MetricHistoryView(DetailView):
    template_name = 'hmeter_frontend/project/metric-history.html'
    context_object_name = 'project'
    model = Project

    def get_context_data(self, **kwargs):
        data = super(MetricHistoryView, self).get_context_data(**kwargs)

        base_qs = MetricCache.objects.filter(project=self.object,
                                             end__isnull=False)
        data['dates'] = base_qs.values_list('end', flat=True) \
                               .order_by('end') \
                               .distinct()

        data['metricdata'] = base_qs.iter_by_metric(
            ['level', 'title'],
            ['raw_value', 'score'])

        return data
