# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.management.base import ImporterCommand

from healthmeter.downloadinfo.importers import DownloadImporter
from healthmeter.downloadinfo.models import DataSource


class Command(ImporterCommand):
    importer = DownloadImporter
    model = DataSource
