# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import bs4
import logging
import urllib.request
import urllib.parse


logger = logging.getLogger(__name__)


class LinkScraper(object):
    def __init__(self, url, patterns, max_depth=-1):
        self.url = url
        self.parsed_url = urllib.parse.urlparse(url)
        self.patterns = patterns
        self.max_depth = max_depth

        logger.info('Initialized link scraper for %s', self.url)

    def __iter__(self):
        return self.get_links()

    def get_links(self):
        response = urllib.request.urlopen(self.url)
        bs = bs4.BeautifulSoup(response)

        for link in bs.find_all('a'):
            try:
                href = link['href']

            except KeyError:
                # this happens for <a> tags without a href attribute
                continue

            url = urllib.parse.urljoin(self.url, href)
            purl = urllib.parse.urlparse(url)

            # yield matching patterns immediately
            for i in self.patterns:
                if i.search(href):
                    yield url
                    break

            else:
                if ((not purl.path.startswith(self.parsed_url.path) or
                     self.max_depth == 0 or
                     purl.path == self.parsed_url.path)):
                    continue

                for link in LinkScraper(url, self.patterns,
                                        self.max_depth - 1):
                    yield link
