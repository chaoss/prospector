# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging

from .importer import MailImporter, Message


logger = logging.getLogger(__name__)


class MBoxImporter(MailImporter):
    """Mailiing list importer using mbox as input"""

    def get_messages(self):
        """
        Iterate through all messages in self.mbox_file
        """
        messages = self.backend.fetch()

        for message in messages:
            data = message['data']

            try:
                msg = Message(data['From'], data['Date'], data['Subject'],
                              data['Message-ID'], data['References'])
            except:
                logger.warning('Malformed message found, skipping:\n%s', message['updated_on'],
                               exc_info=True)
                msg = None

            # yield outside the try block to avoid capturing exceptions
            # that should terminate the loop instead
            if msg is not None:
                yield msg


MailImporter.register_importer('mbox', MBoxImporter)
