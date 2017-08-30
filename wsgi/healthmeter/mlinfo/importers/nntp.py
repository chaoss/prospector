# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import nntplib
import re
import urllib.parse
from email.parser import HeaderParser

from .importer import MailImporter, Message


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

        self.nntp = nntplib.NNTP(self.server, self.port,
                                 self.username, self.password,
                                 readermode=True)

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

    def close(self):
        """ Quit the NNTP connection"""
        self.nntp.quit()

    def get_messages(self):
        """
        Iterate through all messages in the NNTP group
        """
        (resp, article_count,
         first_article, last_article, _) = self.nntp.group(self.group)

        try:
            article_id = first_article
            while True:
                msg = HeaderParser().parsestr(
                    "\r\n".join(self.nntp.head(article_id)[3]))

                msg['Message-Id'] = self.gmane_mangler_regex.sub(
                    '', msg['Message-Id'])

                yield Message(msg['From'], msg['Date'], msg['Subject'],
                              msg['Message-Id'], msg['References'])

                _, article_id, _ = self.nntp.next()

        except nntplib.NNTPTemporaryError as e:
            if e.message != '421 No next article to retrieve':
                raise

MailImporter.register_importer('nntp', NntpImporter)
