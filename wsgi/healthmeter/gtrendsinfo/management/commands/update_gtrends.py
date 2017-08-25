# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.gtrendsinfo.importers import GTrendsImporter
from healthmeter.gtrendsinfo.models import Query

from healthmeter.importerutils.management.base import ImporterCommand

import itertools


class Command(ImporterCommand):
    importer = GTrendsImporter
    importer_type = "GTrends"
    model = Query
