# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.importerutils.importers import ImporterBase
from healthmeter.bloginfo.models import Blog


class BlogImporter(ImporterBase):
    """Generic blog post importer class"""
    model = Blog

    @classmethod
    def resolve_importer_type(cls, blog):
        return 'rss'
