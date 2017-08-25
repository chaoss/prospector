# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from collections import namedtuple
from django.http import Http404
from django.views.generic import TemplateView
import itertools
import json

from healthmeter.utils import pairwise

from ...models import Project, MetricCache
from ...metrics.lookup import get_metricunit

MetricEntry = namedtuple('MetricEntry', ['name', 'level', 'metric_colour',
                                         'datalist'])
MetricData = namedtuple('MetricData', ['score', 'value', 'unit'])


class CompareProject(TemplateView):
    template_name = 'hmeter_frontend/project/compare.html'

    def get_context_data(self, **kwargs):
        data = super(CompareProject, self).get_context_data(**kwargs)

        project_ids = [int(id_) for id_ in kwargs['ids'].split(',')]
        project_map = Project.objects.in_bulk(project_ids)

        if len(set(project_ids)) != len(project_map):
            raise Http404

        # Display project in order that it came in
        projects = [project_map[id_] for id_ in project_ids]

        # Assertion is fine here -- urls.py should ensure this.
        assert len(projects) > 1, "Must have more than one project to compare"

        data['projects'] = projects
        it = MetricCache.objects \
                        .filter(project__in=projects, end__isnull=True) \
                        .iter_by_metric(['level', 'title', 'algorithm__name',
                                         'colour', 'time_based'],
                                        ['project', 'score', 'raw_value'],
                                        ('project', project_ids))

        def iter_score_breakdown():
            for metric in it:
                for data in metric.datalist:
                    data.unit = get_metricunit(metric.algorithm__name,
                                               data.raw_value)

                yield metric

        l1metrics, metrics = itertools.tee(iter_score_breakdown())
        l1metrics = (m for m in l1metrics if m.level == 1)

        def gen_score_breakdown():
            for current_entry, next_entry in pairwise(metrics):
                if current_entry is None:
                    continue

                current_entry.has_children = (
                    next_entry is not None and
                    current_entry.level < next_entry.level
                )

                yield current_entry

        data['score_breakdown'] = gen_score_breakdown()
        data['l1_score_breakdown'] = l1metrics

        return data
