# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.views.generic import ListView
from healthmeter.hmeter_frontend.models import Project
from healthmeter.utils import djcached


class ProblematicProjects(ListView):
    template_name = 'hmeter_frontend/project/problems.html'
    context_object_name = 'project_problems'

    def iter_project_problems(self):
        for project in Project.objects.filter(parent=None).iterator():
            problems = []

            if project.is_wip:
                problems.append("Marked as work in progress")

            resources = (
                (project.all_vcs_repositories, 'VCS commits', {}),
                (project.all_bug_trackers, 'bug reports', {}),
                (project.all_mailing_lists, 'mailing list posts', {}),
                (project.all_blogs, 'blogs', {}),
            )

            for res, desc, kwargs in resources:
                if res.filter(last_updated=None, **kwargs).exists():
                    problems.append("Import of {0} not complete".format(desc))

            if problems:
                yield project, problems

    @djcached('problematic_projects', 6 * 60 * 60)
    def get_queryset(self):
        return list(self.iter_project_problems())
