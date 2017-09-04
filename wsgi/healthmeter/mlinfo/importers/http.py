# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging
import re

from perceval.backends.core.pipermail import Pipermail

from .importer import MailImporter
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
        super().__init__(mailing_list)
        self.username = username
        self.password = password

        self.mailing_list_path = get_mailing_list_path(mailing_list)

        self.backend = Pipermail(mailing_list.archive_url,
                                 self.mailing_list_path)

MailImporter.register_importer('http', HttpImporter)
MailImporter.register_importer('https', HttpImporter)
