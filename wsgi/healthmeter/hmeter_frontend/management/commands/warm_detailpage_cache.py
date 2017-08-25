# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.management.base import BaseCommand, CommandError

from healthmeter.hmeter_frontend.models import Project
from healthmeter.hmeter_frontend.views.project.detail import ProjectDetail


class Command(BaseCommand):
    args = '[<project_id>...]'
    help = 'Updates the ProjectDetail view cache'

    def handle(self, *args, **options):
        projects = list(Project.objects.filter(id__in=args) if args
                        else Project.objects.root_nodes())

        for project in projects:
            view = ProjectDetail()
            view.object = project
            view.get_projdata(_djcached_force_recache=True)
