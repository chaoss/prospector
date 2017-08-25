# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.importers import ImporterBase
from healthmeter.downloadinfo.models import DataSource


class DownloadImporter(ImporterBase):
    model = DataSource

    @classmethod
    def resolve_importer_type(cls, obj):
        return obj.format.name
