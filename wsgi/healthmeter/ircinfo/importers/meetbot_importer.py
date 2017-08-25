# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
import logging
import os
import re
import urllib2
import urlparse

from healthmeter.hmeter_frontend.utils import LinkScraper

from .common import IrcImporter, IrcLogParser

logger = logging.getLogger(__name__)


class MeetbotIrcImporter(IrcImporter):
    rawlog_pattern = re.compile(r'(?P<date>\d{4}-\d{2}-\d{2}-\d{2}\.\d{2})'
                                '\.log\.txt$')

    def __init__(self, irc_channel):
        super(MeetbotIrcImporter, self).__init__(irc_channel)
        self.scraper = (LinkScraper(self.irc_channel.meeting_logs_url,
                                    (self.rawlog_pattern,), 2)
                        if irc_channel.meeting_logs_url else None)

        if self.scraper:
            logger.info('Initialized MeetbotIrcImporter for channel [%s]',
                        irc_channel)
        else:
            logger.info("Skipping MeetbotIrcImporter run for channel [%s]:"
                        "No meeting logs url", irc_channel)

    def _run(self):
        if not self.scraper:
            return

        for link in self.scraper.get_links():
            logger.info('Got link [%s]: ', link)
            filename = os.path.basename(urlparse.urlparse(link).path)
            datestring = self.rawlog_pattern.search(filename).group('date')
            base_timestamp = datetime.datetime.strptime(datestring,
                                                        '%Y-%m-%d-%H.%M')

            # Initialize timestamp to base_timestamp to make sure it's defined
            timestamp = base_timestamp
            irc_message_ids = []

            # Skip if we've got an irc meeting at this channel starting at the
            # same time
            if self.irc_channel.meetings.filter(time_start=base_timestamp) \
                                        .exists():
                logger.info('Found meeting at %s. Skipping.', datestring)
                continue

            with IrcLogParser(urllib2.urlopen(link)) as logparser:
                for nickname, t, _ in logparser:
                    author = self._get_irclogin_obj(nickname)
                    timestamp = base_timestamp.replace(hour=t.hour,
                                                       minute=t.minute,
                                                       second=t.second)
                    msg = self.irc_channel.messages.create(
                        author=author, timestamp=timestamp,
                        channel=self.irc_channel)

                    irc_message_ids.append(msg.pk)
                    logger.debug('Imported IRC message [%s]', msg)

            # Last message timestamp is when the meeting ends
            meeting, created = self.irc_channel.meetings.get_or_create(
                time_start=base_timestamp, time_end=timestamp)

            # Delete all previously imported messages in this time range if
            # they exist. Since Meetbot's raw logs contain all the messages
            # during the meeting, we should only have the messages we have
            # imported during this time.
            meeting.get_messages().exclude(pk__in=irc_message_ids).delete()

            if created:
                self.record_timestamp(meeting.time_start)
                self.record_timestamp(meeting.time_end)

IrcImporter.register_importer('meetbot', MeetbotIrcImporter)
