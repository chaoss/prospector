# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase

from .models import *


class TestPurpose(TestCase):
    def test_unicode(self):
        p = Purpose.objects.create(name='user')
        self.assertEqual(unicode(p), u'user')

    def test_duplicate(self):
        p = Purpose.objects.create(name='user')

        with self.assertRaises(IntegrityError):
            Purpose.objects.create(name='user')


class TestMailingList(TransactionTestCase):
    def test_unicode(self):
        m = MailingList.objects.create(posting_address='test@example.com',
                                       archive_url='http://example.com')

        self.assertEqual(unicode(m), 'test@example.com')

    def test_duplicate(self):
        posting_address = 'test@example.com'
        archive_url = 'http://example.com'

        m = MailingList.objects.create(posting_address=posting_address,
                                       archive_url=archive_url)

        with self.assertRaises(IntegrityError):
            MailingList.objects.create(posting_address=posting_address,
                                       archive_url='http://other.example.com')

    def test_emptyfield(self):
        sid = transaction.savepoint()
        with self.assertRaises(IntegrityError):
            MailingList.objects.create(posting_address='test@example.com',
                                       archive_url=None)
        transaction.savepoint_rollback(sid)

        with self.assertRaises(IntegrityError):
            MailingList.objects.create(posting_address=None,
                                       archive_url='http://example.com')


class TestPost(TransactionTestCase):
    def _get_mailinglist(self):
        return MailingList.objects.get_or_create(
            posting_address='test@example.com',
            archive_url='http://example.com')[0]

    def _get_participant(self):
        return Participant.objects.get_or_create(name='test')[0]

    def _get_post(self, msgid):
        m = self._get_mailinglist()
        p = self._get_participant()

        return m.posts.create(author=p, timestamp=datetime.datetime.utcnow(),
                              subject='', message_id=msgid)

    def test_unicode(self):
        msgid = 'abc'
        post = self._get_post(msgid)
        self.assertEqual(unicode(post), msgid)

    def test_duplicate(self):
        msgid = 'abc'
        post1 = self._get_post(msgid)

        post2 = self._get_post('def')

        self.assertNotEqual(post1.id, post2.id)

        with self.assertRaises(IntegrityError):
            self._get_post(msgid)

    def test_emptyfield(self):
        m = self._get_mailinglist()
        p = self._get_participant()

        values = {
            'author': p,
            'timestamp': datetime.datetime.utcnow(),
            'subject': '',
            'message_id': 'abc'
        }

        for key in values:
            kwargs = values.copy()
            kwargs[key] = None

            sid = transaction.savepoint()
            with self.assertRaises(ValueError if key == 'author'
                                   else IntegrityError):
                # ForeignKeys throw a ValueError instead of IntegrityError.
                Post.objects.create(**kwargs)
            transaction.savepoint_rollback(sid)
