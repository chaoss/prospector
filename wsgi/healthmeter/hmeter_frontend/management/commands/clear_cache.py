# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache


class Command(BaseCommand):
    args = '<key>...'
    help = 'Clear cache keys by setting them to None'

    def handle(self, *args, **options):
        cache.set_many(dict((key, None) for key in args))
