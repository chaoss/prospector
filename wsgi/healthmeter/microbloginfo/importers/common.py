# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.importers import ImporterBase
from healthmeter.microbloginfo.models import Microblog


class MicroblogImporter(ImporterBase):
    """Generic blog post importer class"""
    model = Microblog

    @classmethod
    def resolve_importer_type(cls, ublog):
        return ublog.provider.name
