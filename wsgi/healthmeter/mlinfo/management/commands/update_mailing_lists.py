# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from healthmeter.mlinfo.importers import MailImporter
from healthmeter.mlinfo.models import MailingList

from healthmeter.importerutils.management.base import ImporterCommand


class Command(ImporterCommand):
    importer = MailImporter
    model = MailingList
