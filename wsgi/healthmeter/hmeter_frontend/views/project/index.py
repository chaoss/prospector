# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
from django.db.models import Max, Min
from django.views.generic import ListView
from django.utils.safestring import mark_safe
import simplejson

from healthmeter.utils import djcached, ProxyObject
from healthmeter.hmeter_frontend.utils.stats import max_or_none, min_or_none
import itertools
from ...models import Project, Metric


class ProjectIndex(ListView):
    model = Project
    template_name = 'hmeter_frontend/project/index.html'
    context_object_name = 'projects'

    def get_context_data(self, *args, **kwargs):
        data = super(ProjectIndex, self).get_context_data(*args, **kwargs)

        data['l1_metrics'] = Metric.objects.filter(level=1).order_by('lft')
        data['descriptions'] = dict((project.id, project.description)
                                    for project in data['projects'])

        return data

    @djcached("project:roots_list", 3600)
    def get_queryset(self):
        return Project.objects.filter(parent__isnull=True) \
                              .order_by('name') \
                              .prefetch_dates() \
                              .with_l1_scores()
