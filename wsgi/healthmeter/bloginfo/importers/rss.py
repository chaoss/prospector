# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging
from email.utils import parseaddr

import grimoirelab.toolkit.datetime
import perceval.backends.core.rss as rss_importer

from healthmeter.hmeter_frontend.utils import get_participant

from .common import BlogImporter

logger = logging.getLogger(__name__)


class RSSImporter(BlogImporter):
    """Blog importer class that imports things from RSS feeds"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def parse_date(timestamp):
        return grimoirelab.toolkit.datetime.unixtime_to_datetime(timestamp)

    @staticmethod
    def get_participant(author):
        name, email = parseaddr(author)

        return get_participant(name, email) if '@' in email else None

    @staticmethod
    def extract_timestamp(item):
        return RSSImporter.parse_date(item['updated_on'])

    @staticmethod
    def extract_author(item):
        try:
            return RSSImporter.get_participant(item['data']['author'])
        except KeyError:
            return None

    @staticmethod
    def extract_guid(item):
        data = item['data']
        return (data.get('id') or data.get('link') or
                (data.get('enclosures') and data['enclosures'][0]['href']) or
                data.get('title'))

    def _run(self):
        """Import all blog posts from aforementioned post"""
        logger.info("Importing blog posts from [%s] using feed URL [%s]",
                    self.object, self.object.rss_url)

        backend = rss_importer.RSS(self.object.rss_url)
        items = backend.fetch()

        for item in items:
            logger.info("Beginning to parse feed item")

            blogpost, created = self.object.posts.get_or_create(
                guid=self.extract_guid(item),
                defaults={
                    'timestamp': self.extract_timestamp(item),
                    'author': self.extract_author(item),
                    'title': item['data']['title']
                })

            updated = created

            if created:
                logger.info("Imported blog post [%s]", blogpost)
            elif blogpost.title != item['data']['title']:
                updated = True
                logger.info("Updating title of blog post [%s] from [%s] to "
                            "[%s]",
                            blogpost, blogpost.title, item['data']['title'])
                blogpost.title = item['data']['title']
                blogpost.save()

            if updated:
                self.record_timestamp(blogpost.timestamp)

BlogImporter.register_importer('rss', RSSImporter)
