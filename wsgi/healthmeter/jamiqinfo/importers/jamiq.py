# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
import datetime
import functools
import iso8601
import itertools
import logging
import requests
import simplejson

from healthmeter.importerutils.importers import ImporterBase
from healthmeter.jamiqinfo.models import Topic
from healthmeter.utils import pairwise

logger = logging.getLogger(__name__)


class JamiqError(Exception):
    @property
    def text(self):
        return self.args[1]

    @property
    def status(self):
        return self.args[0]


class JamiqImporter(ImporterBase):
    model = Topic

    def __init__(self, topic,
                 queryurl='https://api.jamiq.com/buzz/v2/topic/query'):
        super(JamiqImporter, self).__init__(topic)
        self.queryurl = queryurl
        self.auth = (topic.credential.username, topic.credential.password)

    def _perform(self, data):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        tries = 10

        while tries > 0:
            response = requests.post(self.queryurl,
                                     data=simplejson.dumps(data),
                                     headers=headers,
                                     verify=False,
                                     auth=self.auth)
            if response.status_code == 504:  # gateway timeout
                tries -= 1
            else:
                break

        if response.status_code != 200:
            raise JamiqError(response.status_code, response.text)

        return response.json()

    def import_data(self, start, end, strip_zeros):
        def toiso8601(date):
            return datetime.datetime.combine(date,
                                             datetime.time(
                                                 tzinfo=iso8601.iso8601.UTC)) \
                                    .isoformat()

        query = {
            'filter_by': {
                'topic_id': [self.object.topic_id],
                'start_date': toiso8601(start),
                'end_date': toiso8601(end)
            },

            'grouping': {
                'by': 'content_date',
                'gap': '+1day'
            }
        }

        thresholds = (2.0 / 3 - 1, 2.0 * 2 / 3 - 1)
        classification = ('negative', 'neutral', 'positive')
        data = collections.defaultdict(
            functools.partial(collections.defaultdict, int)
        )

        for (lower, upper), cls in itertools.izip(pairwise(thresholds),
                                                  classification):
            sentiment_filter = []
            lower = -1.0 if lower is None else lower
            upper = 1.0 if upper is None else upper

            sentiment_filter.append('>= ' + str(lower))
            sentiment_filter.append('<= ' + str(upper))

            query['filter_by']['content_sentiment_score'] = sentiment_filter

            result = self._perform(query)['results']

            found = False
            for date, count in result:
                if strip_zeros and count == 0 and not found:
                    continue

                found = True
                data[date][cls] = count

        for date, counts in data.iteritems():
            date = iso8601.parse_date(date).date()
            dp, created = self.object.datapoints.get_or_create(
                datestamp=date,
                defaults={
                    'positive_sentiment_count': counts['positive'],
                    'neutral_sentiment_count': counts['neutral'],
                    'negative_sentiment_count': counts['negative']
                }
            )

            logger.info("%s datapoint %s",
                        "Imported" if created else "Found",
                        dp)

            dirty = False
            if not created:
                for k, v in counts.items():
                    if getattr(dp, k + '_sentiment_count') != v:
                        dirty = True
                        setattr(dp, k + '_sentiment_count', v)

                if dirty:
                    dp.save()

            if created or dirty:
                self.record_timestamp(date)

        return bool(data)

    def _run(self):
        logger.info("Starting import for topic [%s]",
                    self.object)
        day = datetime.timedelta(days=1)

        try:
            current = (self.object.datapoints.latest('datestamp').datestamp +
                       day)
            found_dp = True

        except self.object.datapoints.model.DoesNotExist:
            current = datetime.date(1970, 1, 1)
            found_dp = False

        today = datetime.date.today()

        start = current
        step = datetime.timedelta(days=90)
        strip_zeros = not found_dp
        while start < today:
            end = min(today, start + step)

            logger.info("Importing data for range %s -> %s, strip_zeros=%s",
                        start, end, strip_zeros)
            if self.import_data(start, end, strip_zeros):
                strip_zeros = False
            start = end

    @classmethod
    def resolve_importer_type(cls, obj):
        return 'jamiq'


JamiqImporter.register_importer('jamiq', JamiqImporter)
