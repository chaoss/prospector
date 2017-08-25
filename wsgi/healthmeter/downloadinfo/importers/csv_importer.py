# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import csv
import cStringIO
from django.db import transaction
import logging
import requests
from .common import DownloadImporter

logger = logging.getLogger(__name__)


class CsvDownloadImporter(DownloadImporter):
    def _run(self):
        contents = requests.get(self.object.url).text
        contents_fileobj = cStringIO.StringIO(contents)
        for entry in csv.DictReader(contents_fileobj, ('date', 'count')):
            dp, created = self.object.datapoints.get_or_create(
                date=entry['date'],
                defaults=dict(downloads=entry['count']))

            if not created and dp.downloads != entry['count']:
                logger.warn("Downloads for [%s] don't match DB. Fixing DB.",
                            dp)
                dp.downloads = entry['count']
                dp.save()
                self.record_timestamp(dp.date)

            elif created:
                self.record_timestamp(dp.date)

DownloadImporter.register_importer('csv', CsvDownloadImporter)
