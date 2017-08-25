# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.management.base import ImporterCommand

from healthmeter.vcsinfo.importers import VcsImporter
from healthmeter.vcsinfo.models import Repository


class Command(ImporterCommand):
    importer = VcsImporter
    model = Repository
