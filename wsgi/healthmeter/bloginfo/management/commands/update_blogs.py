# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.bloginfo.importers import BlogImporter
from healthmeter.bloginfo.models import Blog

from healthmeter.importerutils.management.base import ImporterCommand


class Command(ImporterCommand):
    importer = BlogImporter
    model = Blog
