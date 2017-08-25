# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.btinfo.models import BugNamespace
from healthmeter.btinfo.importers.mantis_importer import MantisImporter
MantisImporter(BugNamespace.objects.get(id=345)).run()
