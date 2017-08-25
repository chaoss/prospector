# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.jamiqinfo.importers.jamiq import JamiqImporter
from healthmeter.jamiqinfo.models import Topic

from healthmeter.importerutils.management.base import ImporterCommand


class Command(ImporterCommand):
    importer = JamiqImporter
    model = Topic
