# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.core.urlresolvers import normalize, reverse, NoReverseMatch
from healthmeter.hmeter_frontend.renderers import ProjectRenderer
import itertools


class Command(BaseCommand):
    args = '<project_id> [<project_id>...]'

    def handle(self, *projids, **_):
        if not projids:
            raise CommandError("Need to supply at least one project id")

        paths = reduce(lambda x, y: x | y,
                       (ProjectRenderer.get_paths_for_project(projid)
                        for projid in projids))

        call_command('render_paths', *paths)
