# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import set_script_prefix
from healthmeter.hmeter_frontend.renderers import ManualRenderer


class Command(BaseCommand):
    args = '<path> [<path>...]'
    help = 'Renderes on path using medusa'

    def handle(self, *paths, **_):
        if not paths:
            raise CommandError("Need to supply at least one path to render.")

        url_prefix = getattr(settings, 'MEDUSA_URL_PREFIX', None)
        if url_prefix is not None:
            set_script_prefix(url_prefix)

        ManualRenderer.initialize_output()
        renderer = ManualRenderer(paths)
        renderer.generate()
        ManualRenderer.finalize_output()
