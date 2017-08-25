# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from dateutil import parser as dateparser, tz
from email.utils import parseaddr
from calendar import timegm
from collections import defaultdict
import datetime
import logging
import re
import urlparse

from django.db import IntegrityError, transaction

from healthmeter.mlinfo import models as mlmodels
from healthmeter.importerutils.importers import ImporterBase
from healthmeter.hmeter_frontend.utils import (get_participant,
                                               undo_antispam_mangling,
                                               coerce_unicode)

logger = logging.getLogger(__name__)


class MissingRef(Exception):
    """Exception class that indicates a missing reference"""
    def __init__(self, missing_refs):
        self.missing_refs = missing_refs
        super(MissingRef, self).__init__(missing_refs)


class MailImporter(ImporterBase):
    """
    Generic mail importer class to be derived from to implement individual
    importers.
    """
    model = mlmodels.MailingList

    @classmethod
    def resolve_importer_type(cls, mailing_list):
        return urlparse.urlparse(mailing_list.archive_url).scheme

    def get_messages(self):
        """
        Empty generator stub, should be implemented in specialized importer
        clases either as a function that returns an iterable object, or as a
        generator itself.
        """
        if False:
            yield

    def _save_message(self, msg, waiting_refs):
        """
        Save `msg' as well as all messages waiting for it under `waiting_refs'
        into the database.

        @arg msg            Message to save
        @arg waiting_refs   Dict of msgids to sets of messages waiting for them
        """
        ready_messages = [msg]

        while ready_messages:
            msg = ready_messages.pop(0)

            try:
                msg.save_to_db(self.object, self)

                for msg2 in waiting_refs[msg.msgid]:
                    ready_messages.append(msg2)

                del waiting_refs[msg.msgid]

            except MissingRef, e:
                for ref in e.missing_refs:
                    waiting_refs[ref].add(msg)

            except:
                logger.error('Could not import message, skipping: %s',
                             msg, exc_info=True)

    def _run(self):
        """
        Import messages into the database under ``self.object''. Makes
        use of ``self.get_messages()'' to obtain messages to import.
        """

        waiting_refs = defaultdict(set)

        for msg in self.get_messages():
            self._save_message(msg, waiting_refs)

        if waiting_refs:
            # Collect the really-missing refs that are really not present...
            missing_refs = set(waiting_refs.keys())
            missing_refs -= set((msg.msgid
                                 for ref in missing_refs
                                 for msg in waiting_refs[ref]))

            # ...and drop them. The rest can be then added to the database
            root_messages = []

            for ref in missing_refs:
                logger.warn("Referenced message [%s] not found in database or "
                            "imported archive, ignoring", ref)

                for msg in waiting_refs[ref]:
                    if not msg.ignore_ref(ref):
                        root_messages.append(msg)

                del waiting_refs[ref]

            for msg in root_messages:
                self._save_message(msg, waiting_refs)

        assert not waiting_refs


class Message:
    """
    Message class for storing information on a message. Accessible data members
    are:
    - author_email: str containing email from the From field
    - author_name: str containing name portion of From field
    - timestamp: datetime.datetime representing Date field
    - subject: str containing subject of message
    - msgid: str containing value of the Message-Id field
    - references: A set() containing the msgid's from the References field
    """
    author_email = ''
    author_name = ''
    timestamp = None
    subject = ''
    msgid = ''
    references = set()
    found_refs = set()
    missing_refs = set()

    msgid_regex = re.compile(r'<[^>]+>')
    tzcomment_regex = re.compile(r'((?:\+|-)[0-9]{4}) \([^)]+\)$')

    def __init__(self, author, timestamp, subject, msgid, references):
        """
        author: email string of author, e.g. "Foo Bar <foo.bar@example.com>"
        timestamp: string containing Date field of the message
        subject: string containing subject of the message
        msgid: string containing Message-Id field of the message
        references: set of msgid strings in References field of message
        """
        args = [author, timestamp, subject, msgid]
        if None in args:
            argname = ['author', 'timestamp',
                       'subject', 'msgid'][args.index(None)]

            raise ValueError(
                "Cannot construct Message: {0} is None".format(argname))

        if '@' not in author:
            author = undo_antispam_mangling(author)

        self.author_name, self.author_email = map(coerce_unicode,
                                                  parseaddr(author))

        # dateutil.parser breaks on timezones like +0000 (FOO BAR)
        timestamp = self.tzcomment_regex.sub(r'\1', timestamp)
        self.timestamp = dateparser.parse(timestamp)

        if self.timestamp.tzinfo:
            self.timestamp = self.timestamp \
                                 .astimezone(tz.tzutc()) \
                                 .replace(tzinfo=None)

        # Check for invalid date and fall back upon from_string
        if self.timestamp.year < 1970:
            raise ValueError("Email from before the beginning of time")

        self.subject = subject
        self.msgid = msgid

        if not references:
            self.references = set()

        else:
            self.references = set(self.msgid_regex.findall(references))

    def __str__(self):
        return self.msgid

    def get_participant(self):
        """
        Get participant or create corresponding participant for author of this
        message.
        """
        return get_participant(self.author_name, self.author_email)

    def get_references(self):
        """
        Get mlinfo.models.Post objects corresponding to self.references. Raises
        ``MissingRef'' if there are missing references.
        """
        djrefs = mlmodels.Post.objects.filter(message_id__in=self.references)

        # message_id is a unique column, so the set is complete if the length
        # is equal
        if djrefs.count() == len(self.references):
            return djrefs

        else:
            self.found_refs = set((ref.message_id for ref in djrefs))
            self.missing_refs = self.references - self.found_refs

            raise MissingRef(self.missing_refs)

    def unwait_ref(self, msgid):
        """
        Stop waiting on msgid. Returns remaining missing refs
        """
        self.missing_refs.remove(msgid)
        self.found_refs.add(msgid)

        return self.missing_refs

    def ignore_ref(self, msgid):
        """
        Completely remove msgid from references. Returns remaining missing refs
        """
        self.references.remove(msgid)
        self.missing_refs.remove(msgid)

        return self.missing_refs

    @transaction.atomic
    def save_to_db(self, mailing_list, importer):
        """
        Save this message to database under ``mailing_list''. If a message with
        the same message-id is already in the database, add the message to this
        ``mailing list''.
        """
        author = self.get_participant()

        try:
            with transaction.atomic():
                post = mlmodels.Post.objects.create(
                    author=author,
                    timestamp=self.timestamp,
                    subject=self.subject,
                    message_id=self.msgid)
                post.references.add(*self.get_references())
                post.mailing_lists.add(mailing_list)

                importer.record_timestamp(post.timestamp)

                logger.info("Imported message [%s]", self.msgid)

        except IntegrityError:
            try:
                post = mailing_list.posts.filter(message_id=self.msgid)
                logger.info("Message [%s] already registered under [%s]. Not "
                            "doing anything..", post, mailing_list)
            except mailing_list.DoesNotExist:
                post = mlmodels.Post.objects.get(message_id=self.msgid)
                logger.info("Found message [%s], adding to mailing list",
                            self.msgid)
                post.mailing_lists.add(mailing_list)
                importer.record_timestamp(post.timestamp)

        return post
