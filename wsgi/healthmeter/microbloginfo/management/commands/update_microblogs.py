# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.microbloginfo.importers import MicroblogImporter
from healthmeter.microbloginfo.models import Microblog

from healthmeter.importerutils.management.base import ImporterCommand


class Command(ImporterCommand):
    importer = MicroblogImporter
    model = Microblog
