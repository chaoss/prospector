# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.views.generic import TemplateView
from collections import namedtuple
import os
import glob
import json
from itertools import chain
from healthmeter.hmeter_frontend.models import Project
from healthmeter.hmeter_frontend.utils.iterators import uniq


ProjectInfo = namedtuple('ProjectInfo', ['name', 'external', 'link', 'id'])


class AllProjectsView(TemplateView):
    template_name = 'hmeter_frontend/all-projects.html'

    def get_context_data(self, **kwargs):
        data = super(AllProjectsView, self).get_context_data(**kwargs)

        json_files = glob.glob(
            os.path.join(os.path.dirname(__file__), '*.json'))

        def gen_project_lists():
            for f in map(open, json_files):
                with f:
                    yield json.load(f)

        project_keyfn = lambda x: x[0].lower()
        projects = uniq(
            sorted(chain(*gen_project_lists()), key=project_keyfn),
            key=project_keyfn
        )

        treeid_lookup = dict((p.tree_id, p.id)
                             for p in Project.objects.filter(parent=None))

        djprojects = dict(
            (p.name.lower(), treeid_lookup[p.tree_id])
            for p in Project.objects.all()
        )

        def gen_projects():
            for project, link in projects:
                try:
                    id_ = djprojects[project.lower()]

                except KeyError:
                    id_ = None

                yield ProjectInfo(project, id_ is None, link, id_)

        data['projects'] = list(gen_projects())

        return data
