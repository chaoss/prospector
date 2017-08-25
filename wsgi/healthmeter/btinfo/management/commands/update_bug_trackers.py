# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.management.base import ImporterCommand
from healthmeter.btinfo.importers import BugTrackerImporter
from healthmeter.btinfo.models import BugNamespace


class Command(ImporterCommand):
    importer = BugTrackerImporter
    model = BugNamespace
