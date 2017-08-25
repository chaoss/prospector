# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
Importer for Google Trends information. Uses a singleton-like structure similar
to CVEs because it's more efficient to do this in one round. Either way, we'll
probably be banned 5 queries in, and have to wait for the next round.
"""

import csv
from cStringIO import StringIO
import ctypes
import datetime
from django.db import transaction
import logging
import multiprocessing

from pyGoogleTrendsCsvDownloader import (pyGoogleTrendsCsvDownloader,
                                         QuotaExceeded)

from healthmeter.gtrendsinfo.models import Credential, Query
from healthmeter.importerutils.importers import ImporterBase

logger = logging.getLogger(__name__)


class GTrendsImporter(ImporterBase):
    model = Query
    quota_exceeded = multiprocessing.Value(ctypes.c_bool, False)

    @classmethod
    def resolve_importer_type(cls, gtrendsquery):
        return 'gtrends'

    def __init__(self, *args, **kwargs):
        super(GTrendsImporter, self).__init__(*args, **kwargs)

        if self.quota_exceeded.value:
            raise QuotaExceeded("Exceeded GTrends query limit. "
                                "Refusing to construct GTrends importer.")

        credentials = Credential.objects.get()
        self.downloader = pyGoogleTrendsCsvDownloader(credentials.username,
                                                      credentials.password)
        # Delay importer download attempts by ~5 seconds
        self.downloader.download_delay = 5

    @staticmethod
    def parse_date(s):
        try:
            return datetime.datetime.strptime(s, "%Y-%m-%d").date()

        except ValueError:
            return datetime.datetime.strptime(s, "%Y-%m").date()

    @staticmethod
    def parse_gtrends_csv(fileobj):
        reader = csv.reader(fileobj)
        for row in reader:
            try:
                range_, count = row
                count = int(count)
                start, end = range_.split(' - ')
                start, end = map(GTrendsImporter.parse_date, (start, end))
                yield start, end, count

            except ValueError:
                pass

    def _run(self):
        logger.info("Getting CSV for query [%s]", self.object)
        try:
            data = StringIO(
                self.downloader.get_csv_data(q=self.object.keyword))
        except QuotaExceeded:
            self.quota_exceeded.value = True

            logger.error("Exceeded GTrends query limit for today. Skipping..")
            raise

        logger.info("Got data! Parsing...")
        logger.debug("Data is\n=====\n%s\n=====", data)

        with transaction.atomic():
            for start, end, count in self.parse_gtrends_csv(data):
                dp, created = self.object.datapoints \
                                  .get_or_create(start=start,
                                                 end=end,
                                                 defaults={'count': count})

                logger.info("%s datapoint: %s",
                            "Created" if created else "Found",
                            dp)

                imported_point = False

                if not created and dp.count != count:
                    logger.info("Updating datapoint count: %s -> %s",
                                dp.count, count)
                    dp.count = count
                    dp.save()

                    imported_point = True

                elif created:
                    imported_point = True

                if imported_point:
                    self.record_timestamp(start)
                    self.record_timestamp(end)

GTrendsImporter.register_importer('gtrends', GTrendsImporter)
