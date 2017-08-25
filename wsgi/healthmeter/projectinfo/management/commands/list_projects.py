# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from ...models import Project


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--all', '-a',
                    dest='all',
                    default=False, action='store_true',
                    help=("Select all projects. If this flag isn't provided, "
                          "then only list root projects.")),
    )
    args = '[--all]'
    help = "List project IDs present in the database, one per line."

    def handle(self, **kwargs):
        getall = kwargs['all']

        qs = Project.objects.all() if getall else Project.objects.root_nodes()
        ids = (str(pid) for pid in qs.values_list('id', flat=True).iterator())

        print('\n'.join(ids))
