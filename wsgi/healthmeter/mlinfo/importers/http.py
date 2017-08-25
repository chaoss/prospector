# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging
import os
import re
import shutil
import urllib2

from healthmeter.hmeter_frontend.utils import (get_decompressed_fileobj,
                                               LinkScraper)

from .importer import MailImporter, Message
from .common import get_mailing_list_path
from .mbox import MBoxImporter

logger = logging.getLogger(__name__)


class HttpImporter(MBoxImporter):
    """
    Mailing list HTML archives scanner. This class scans for mbox files in the
    given URL, downloads them, and hooks up to MBoxImporter to import posts
    into the database.
    """

    url = ''
    username = None
    password = None

    mailing_list_path = ''

    patterns = [re.compile(r'\.(?:txt|mbox)(?:.(?:gz|bz2))?(?:/thread)?$')]

    def __init__(self, mailing_list, username=None, password=None):
        """
        Initializes a HttpImporter instance. It will scan `url' for mbox links
        and download all of them to disk, passing the resulting list of local
        mbox paths to the underlying MBoxImporter object.

        @arg mailing_list   MailingList instance. @see MailImporter
        @arg url            http or https URL to scan
        @arg username       Username to use when requesting url. Will be
                            encoded into POST data as `username'
        @arg password       Password to use when requesting url. Will be
                            encoded into POST data as `password'
        """
        self.username = username
        self.password = password

        self.mailing_list_path = get_mailing_list_path(mailing_list)

        scraper = LinkScraper(mailing_list.archive_url, self.patterns, 0)
        mbox_paths = self.download_mboxes(self.mailing_list_path,
                                          scraper.get_links())

        super(HttpImporter, self).__init__(mailing_list, mbox_paths)

    def download_mboxes(self, save_path, mbox_links):
        """
        Download all mboxes in mbox_links into save_path

        @arg save_path Path to save mboxes into
        @arg mbox_links List of mbox URLs to download
        @return List of downloaded mboxes corresponding to mbox_links
        """

        if self.username:
            postdata = urllib.urlencode({'username': self.username,
                                         'password': self.password})

        else:
            postdata = None

        mbox_paths = []
        for link in mbox_links:
            # Handle mod_mbox links and strip away /thread to get raw mbox
            if link.endswith('/thread'):
                logger.info("Detected mod_mbox link. Stripping /thread")
                link = link[:-len('/thread')]

            logger.info("Downloading [%s]", link)
            try:
                request = urllib2.Request(link, postdata)
                response = urllib2.urlopen(request)

                filename = os.path.basename(link)
                mbox_path = os.path.join(save_path, filename)

                decompressed_response = get_decompressed_fileobj(response)

                with open(mbox_path, 'w') as outf:
                    shutil.copyfileobj(decompressed_response, outf)

                mbox_paths.append(mbox_path)

            except:
                logger.warn("Could not download [%s]. Skipping...",
                            link,
                            exc_info=True)

        return mbox_paths

MailImporter.register_importer('http', HttpImporter)
MailImporter.register_importer('https', HttpImporter)
