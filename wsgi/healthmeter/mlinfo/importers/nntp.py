# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import re
import urllib.parse
import logging

from perceval.backends.core.nntp import NNTP

from .importer import MailImporter, Message


logger = logging.getLogger(__name__)


class NntpImporter(MailImporter):
    """Mailing list importer using NNTP"""

    gmane_mangler_regex = re.compile(r'__[^\$]+\$gmane\$org')

    def __init__(self, mailing_list):
        """
        mailing_list: Mailing list object; See Importer.__init__
        server: NNTP server hostname to connect to
        port: TCP port used to connect to the server
        group: NNTP group on ``server'' to import messages from
        user: Username used to access the server [default: None]
        password: Password used to access the server [default: None]

        This constructs an instance of the NntpImporter to import messages from
        a given group on the NNTP server into the database.
        """
        super().__init__(mailing_list)
        self._parse_url()
        self.backend = NNTP(self.server, self.group)

    def _parse_url(self):
        """
        Parse URL from `self.object' and populate the following fields:
        - self.server
        - self.port
        - self.user
        - self.password
        - self.group
        """
        url = urllib.parse.urlparse(self.object.archive_url)
        assert url.scheme == 'nntp'

        self.group = url.path.lstrip('/')
        self.username = url.username
        self.password = url.password
        self.server = url.hostname
        self.port = url.port if url.port else 119

    def get_messages(self):
        """
        Iterate through all messages in the NNTP group
        """
        articles = self.backend.fetch()

        for article in articles:
            data = article['data']
            data['Message-ID'] = self.gmane_mangler_regex.sub('', data['Message-ID'])

            try:
                msg = Message(data['From'], data['Date'], data['Subject'],
                              data['Message-ID'], data['References'])
            except:
                logger.warning('Malformed message found, skipping:\n%s', article['updated_on'],
                               exc_info=True)
                msg = None

            # yield outside the try block to avoid capturing exceptions
            # that should terminate the loop instead
            if msg is not None:
                yield msg


MailImporter.register_importer('nntp', NntpImporter)
