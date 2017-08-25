# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.db import IntegrityError, transaction
import logging
import re

from healthmeter.importerutils.importers import ImporterBase
from healthmeter.ircinfo.models import Channel
from healthmeter.participantinfo.models import Participant
from healthmeter.ircinfo.models import Meeting, User

logger = logging.getLogger(__name__)


class IrcImporter(ImporterBase):
    model = Channel

    """Base class for irc log importers"""
    def __init__(self, irc_channel):
        """
        Constructor for IrcImporter

        @arg irc_channel ircinfo.models.Channel object
        """
        super(IrcImporter, self).__init__(irc_channel)
        self.irc_channel = irc_channel

    @classmethod
    def resolve_importer_type(cls, irc_channel):
        return 'meetbot'

    @transaction.atomic
    def _get_irclogin_obj(self, nickname):
        """
        Get or create the IrcLogin instance
        """
        # First try to lookup User
        try:
            return User.objects.get(nickname=nickname,
                                    server=self.irc_channel.server)
        except User.DoesNotExist:
            pass

        try:
            with transaction.atomic():
                # Get or create Participant object for Irc user
                participant = Participant.objects.filter(
                    names__name=nickname).first()

                if not participant:
                    participant = Participant.objects.create()
                    participant.names.create(name=nickname)

                # Construct IRC user
                return User.objects.create(participant=participant,
                                           nickname=nickname,
                                           server=self.irc_channel.server)

        # Someone else's won the race. We've bailed out of the previous atomic
        # block, and tossed away that constructed Participant and Name, so try
        # to look up the User again.
        except IntegrityError:
            return User.objects.get(nickname=nickname,
                                    server=self.irc_channel.server)


class IrcLogParser(object):
    """
    Class that wraps a file-like object and parses each line as an IRC log
    line.

    Each line is expected to be in either one of the following formats:
    hh:mm:ss <nickname> message
    hh:mm:ss * nickname message

    Example usage:
    with IrcLogParser(open('/path/to/irclog.txt')) as parser:
        for nickname, timestamp, message in parser:
            pass
    """
    normal_regex = re.compile(r'(?P<timestamp>\d{2}:\d{2}:\d{2}) '
                              '<(?P<nickname>[^>]+)> (?P<message>.*)$')
    action_regex = re.compile(r'(?P<timestamp>\d{2}:\d{2}:\d{2}) \* '
                              '(?P<nickname>[^ ]+) (?P<message>.*)$')

    def __init__(self, file_):
        self.file = file_

    def __iter__(self):
        return self.readlines()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        """ Close the log file to free up resources"""
        self.file.close()

    def readlines(self):
        """
        Generator function that returns (nickname, timestamp, message) for
        every line of the log file.
        """
        for line in self.file:
            for regex in (self.normal_regex, self.action_regex):
                match = regex.match(line)

                if match is not None:
                    break

            # Malformed log line. Ignore
            if match is None:
                logger.warn('Malformed IRC log line found: %s',
                            line)
                continue

            nickname = match.group('nickname')
            timestamp = datetime.datetime.strptime(match.group('timestamp'),
                                                   '%H:%M:%S').time()
            message = match.group('message')

            yield nickname, timestamp, message
