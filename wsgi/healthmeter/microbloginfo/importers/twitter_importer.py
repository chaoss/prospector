# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import IntegrityError, models, transaction, connection
from dateutil.parser import parse as dparse
import logging
import twython
import time
from .common import MicroblogImporter

logger = logging.getLogger(__name__)


class TwitterImporter(MicroblogImporter):
    """
    Twitter backend for microblog importer
    """

    def __init__(self, obj):
        super(TwitterImporter, self).__init__(obj)
        provider = self.object.provider
        self.client = twython.Twython(app_key=provider.username,
                                      app_secret=provider.password)
        self.twitter_handle = self.object.handle

    @transaction.commit_on_success
    def _run(self):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT MAX (int_post_id) AS since_id,
               MIN (int_post_id) - 1 AS max_id
        FROM (
            SELECT CAST (post_id as bigint) AS int_post_id
            FROM microbloginfo_microblogpost
            WHERE microblog_id = %s
        ) subquery
        ''', [self.object.id])

        self.since_id, self.max_id = cursor.fetchone()

        count_after = None
        count_before = None

        # first run
        if self.since_id is None and self.max_id is None:
            self.import_tweets()

        while count_after != 0 or count_before != 0:
            if count_after != 0:
                count_after = self.import_tweets(since_id=self.since_id)

            if count_before != 0:
                count_before = self.import_tweets(max_id=self.max_id)

    def import_tweets(self, **params):
        params['include_rts'] = 1  # include retweets
        params['count'] = 200      # max that twitter allows

        logger.info("Requesting with params %s", params)

        while True:
            try:
                tweets = self.client.get_user_timeline(
                    screen_name=self.twitter_handle,
                    **params)
                break

            except twython.TwythonRateLimitError, e:
                logger.info(
                    "Blocked by twitter rate limit. Waiting for %d seconds.",
                    e.retry_after)
                time.sleep(int(e.retry_after))

        logger.info("Retrieved %d tweets. Loading into db..", len(tweets))

        for tweet in tweets:
            logger.info("Processing tweet %s (%s)", tweet['id'], tweet['text'])
            self.since_id = (max(self.since_id, tweet['id'])
                             if self.since_id is not None else tweet['id'])
            self.max_id = (min(self.max_id, tweet['id'] - 1)
                           if self.max_id is not None else tweet['id'] - 1)

            try:
                with transaction.atomic():
                    self.object.posts.create(
                        post_id=tweet['id'],
                        timestamp=dparse(tweet['created_at']),
                        content=tweet['text'],
                        reposts=tweet['retweet_count'])

                    logger.info("Imported tweet %s into %s", tweet['id'],
                                self.object)

            except IntegrityError, e:
                logger.info("Already imported %s (%s), updating retweet count",
                            tweet['id'], tweet['text'])

                self.object.posts.filter(post_id=tweet['id']).update(
                    reposts=tweet['retweet_count'])

        return len(tweets)

MicroblogImporter.register_importer('twitter', TwitterImporter)
