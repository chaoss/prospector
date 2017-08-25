# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import time
import datetime
import dateutil.parser as dparser
from email.utils import parseaddr
import feedparser
import logging

from healthmeter.hmeter_frontend.utils import get_participant

from .common import BlogImporter

logger = logging.getLogger(__name__)


class RSSImporter(BlogImporter):
    """Blog importer class that imports things from RSS feeds"""

    @staticmethod
    def parse_date(time_tuple):
        return datetime.datetime.fromtimestamp(time.mktime(time_tuple))

    @staticmethod
    def get_participant(author):
        name, email = parseaddr(author)

        return get_participant(name, email) if '@' in email else None

    @staticmethod
    def extract_timestamp(item):
        for field in ('published', 'updated'):
            try:
                parsed_timestamp = item[field + '_parsed']
                if parsed_timestamp:
                    logger.info("Found timestamp in [%s] field: %s",
                                field, parsed_timestamp)
                    return RSSImporter.parse_date(parsed_timestamp)

                else:
                    timestamp = item[field]
                    logger.warn("No parsed timestamp, from feedparser, "
                                "falling back on dateutil.parser: [%s]",
                                timestamp)

                    try:
                        return dparser.parse(timestamp)
                    except ValueError:
                        logger.warn("Invalid timestamp!", field)
            except KeyError:
                pass

        logger.warn("Could not find timestamp, falling back to current time.")
        return RSSImporter.parse_date(datetime.datetime.utcnow())

    @staticmethod
    def extract_author(item):
        try:
            return RSSImporter.get_participant(item['author'])

        except KeyError:
            return None

    @staticmethod
    def extract_guid(item):
        return (item.get('id') or item.get('link') or
                (item.get('enclosures') and
                 item['enclosures'][0]['href']) or
                item.get('title'))

    def _run(self):
        """Import all blog posts from aforementioned post"""
        logger.info("Importing blog posts from [%s] using feed URL [%s]",
                    self.object, self.object.rss_url)
        parsedict = feedparser.parse(self.object.rss_url)
        for item in parsedict['items']:
            logger.info("Beginning to parse feed item")

            blogpost, created = self.object.posts.get_or_create(
                guid=self.extract_guid(item),
                defaults={
                    'timestamp': self.extract_timestamp(item),
                    'author': self.extract_author(item),
                    'title': item['title']
                })

            updated = created

            if created:
                logger.info("Imported blog post [%s]", blogpost)

            elif blogpost.title != item['title']:
                updated = True
                logger.info("Updating title of blog post [%s] from [%s] to "
                            "[%s]",
                            blogpost, blogpost.title, item['title'])
                blogpost.title = item['title']
                blogpost.save()

            if updated:
                self.record_timestamp(blogpost.timestamp)

BlogImporter.register_importer('rss', RSSImporter)
