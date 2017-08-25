# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.cveinfo.importers import CVEImporter
from healthmeter.cveinfo.models import Product

from healthmeter.importerutils.management.base import ImporterCommand


class Command(ImporterCommand):
    importer = CVEImporter
    importer_type = "CVE"
    model = Product
