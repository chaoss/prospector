# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from .models import *


class TestCaseBase(object):
    baseurl = 'https://bugzilla.foo.com/'
    type = 'foo'

    def _get_type(self):
        return Type.objects.get_or_create(name=self.type)[0]

    def _get_bug_tracker(self):
        return BugTracker.objects.get_or_create(
            baseurl=self.baseurl,
            bt_type=self._get_type(),
            username=None,
            password=None)[0]

    def _get_namespace(self):
        tracker = self._get_bug_tracker()
        return tracker.namespaces.get_or_create(product=None,
                                                component=None)[0]

    def _get_bug(self):
        namespace = self._get_namespace()
        return namespace.bugs.get_or_create(
            bug_id='123',
            close_date=datetime.datetime.utcnow())[0]

    def _get_participant(self):
        return Participant.objects.create(name="test")


class TestType(TestCaseBase, TestCase):
    def test_unique(self):
        Type.objects.create(name='foo')

        with self.assertRaises(IntegrityError):
            Type.objects.create(name='foo')

    def test_str(self):
        t = Type.objects.create(name='foo')
        self.assertEqual(t, 'foo')


class TestBugTracker(TestCaseBase, TransactionTestCase):
    def test_unique(self):
        b = self._get_bug_tracker()

        with self.assertRaises(IntegrityError):
            BugTracker.objects.create(baseurl=b.baseurl,
                                      bt_type=b.bt_type)

    def test_str(self):
        b = self._get_bug_tracker()
        self.assertEqual(b, self.baseurl)

    def test_missingfields(self):
        b = BugTracker.objects.create(baseurl=self.baseurl,
                                      bt_type=self._get_type())
        self.assertEqual(None, b.username)
        self.assertEqual(None, b.password)

        with self.assertRaises(IntegrityError):
            sid = transaction.savepoint()
            BugTracker.objects.create(baseurl=None,
                                      bt_type=self._get_type())
        transaction.savepoint_rollback(sid)

        with self.assertRaises(IntegrityError):
            BugTracker.objects.create(baseurl=self.baseurl)


class TestNamespace(TestCaseBase, TestCase):
    def test_str(self):
        bt = self._get_bug_tracker()
        ns = BugNamespace.objects.create(bug_tracker=bt,
                                         product='foo',
                                         component='bar')

        self.assertEqual(ns, '(foo, bar) on %s' % (bt,))

    def test_unique(self):
        bt = self._get_bug_tracker()
        BugNamespace.objects.create(bug_tracker=bt,
                                    product='foo', component='bar')

        with self.assertRaises(IntegrityError):
            BugNamespace.objects.create(bug_tracker=bt,
                                        product='foo', component='bar')


class TestSeverity(TestCase):
    def test_unique(self):
        Severity.objects.create(name="wishlist", level=5)

        with self.assertRaises(IntegrityError):
            Severity.objects.create(name="wishlist", level=5)

    def test_missingfields(self):
        with self.assertRaises(IntegrityError):
            Severity.objects.create(name="wishlist")

    def test_str(self):
        s = Severity(name="wishlist")
        self.assertEqual(s, "wishlist")


class TestBug(TestCaseBase, TestCase):
    def test_unique(self):
        ns = self._get_namespace()
        b = ns.bugs.create(bug_id='123')

        self.assertEqual(ns, b.tracker_info)

        with self.assertRaises(IntegrityError):
            ns.bugs.create(bug_id='123')

    def test_emptyfield(self):
        ns = self._get_namespace()
        with self.assertRaises(IntegrityError):
            ns.bugs.create(bug_id=None)


class TestComment(TestCaseBase, TestCase):
    def test_unique(self):
        bug = self._get_bug()
        author = self._get_participant()

        bug.comments.create(comment_id='456', author=author,
                            timestamp=datetime.datetime.utcnow())

        with self.assertRaises(IntegrityError):
            other_author = Participant.objects.create(name='other')
            bug.comments.create(comment_id='456',
                                author=other_author,
                                timestamp=(datetime.datetime.utcnow() +
                                           datetime.timedelta(days=1)))
