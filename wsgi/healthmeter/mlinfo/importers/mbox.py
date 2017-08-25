# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging
import mailbox

logger = logging.getLogger(__name__)

from .importer import MailImporter, Message


class MBoxImporter(MailImporter):
    """Mailiing list importer using mbox as input"""

    def __init__(self, mailing_list, mbox_files):
        """
        mailing_list: Mailing list object; See Importer.__init__
        mbox_files: List of paths mbox file paths
        """
        super(MBoxImporter, self).__init__(mailing_list)
        self.mboxes = [mailbox.mbox(path) for path in mbox_files]

    def close(self):
        """Close file handles to free up resources"""
        for mbox in self.mboxes:
            mbox.close()

    def get_messages(self):
        """
        Iterate through all messages in self.mbox_file
        """
        for mbox in self.mboxes:
            for msg in mbox:
                try:
                    msg = Message(msg['From'], msg['Date'], msg['Subject'],
                                  msg['Message-Id'], msg['References'])

                except:
                    logger.warn('Malformed message found, skipping:\n%s', msg,
                                exc_info=True)
                    msg = None

                # yield outside the try block to avoid capturing exceptions
                # that should terminate the loop instead
                if msg is not None:
                    yield msg

MailImporter.register_importer('mbox', MBoxImporter)
