# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.jamiqinfo.importers.jamiqtopic import JamiqTopicImporter
from healthmeter.jamiqinfo.models import Credential

from healthmeter.importerutils.management.base import ImporterCommand


class Command(ImporterCommand):
    importer = JamiqTopicImporter
    model = Credential
