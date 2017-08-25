# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.management.base import ImporterCommand

from healthmeter.ircinfo.importers import IrcImporter
from healthmeter.ircinfo.models import Channel


class Command(ImporterCommand):
    importer = IrcImporter
    model = Channel

    def get_queryset(self, args):
        return super(Command, self).get_queryset(args) \
            .exclude(meeting_logs_url=None) \
            .select_related('meetings')
