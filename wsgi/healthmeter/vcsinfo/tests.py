# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
Tests for the vcsinfo app
"""
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase

import datetime

from .models import *


class TestType(TestCase):
    def test_unique(self):
        Type.objects.get(name='git')

        with self.assertRaises(IntegrityError):
            Type.objects.create(name='git')

    def test_unicode(self):
        t = Type.objects.get(name='git')
        self.assertEqual(unicode(t), 'git')


class TestRepository(TestCase):
    def test_duplicate(self):
        t = Type.objects.get(name='git')
        url = 'git://foo/bar.git'

        Repository.objects.create(type=t, url=url)

        with self.assertRaises(IntegrityError):
            Repository.objects.create(type=t, url=url)

    def test_unicode(self):
        t = Type.objects.get(name='git')
        url = 'git://foob/bar.git'
        r = Repository.objects.create(type=t, url=url)

        self.assertEqual(unicode(r), url)


class TestCommit(TestCase):
    def test_duplicate(self):
        t = Type.objects.get(name='git')
        url = 'git://foo/bar.git'
        p = Participant.objects.create(name='test')
        time = datetime.datetime.utcnow()

        r = Repository.objects.create(type=t, url=url)

        committer = Committer.objects.create(participant=p, repository=r,
                                             userid=p.name)

        c = r.commits.create(commit_id='1234', author=committer,
                             timestamp=time)
        self.assertEqual(c.repository, r)
        self.assertIn(c, r.commits.all())

        with self.assertRaises(IntegrityError):
            r.commits.create(commit_id='1234', author=committer,
                             timestamp=time)


class TestBranch(TransactionTestCase):
    def setUp(self):
        self.type = Type.objects.get(name='git')
        self.repository1 = Repository.objects.create(type=self.type,
                                                     url='git://foo/bar.git')
        self.repository2 = Repository.objects.create(type=self.type,
                                                     url='git://bar/baz.git')

        self.participant = Participant.objects.create(name='test')

        time = datetime.datetime.utcnow()
        self.committer1 = self.repository1.committers.create(
            participant=self.participant, userid=self.participant)
        self.commit1 = self.repository1.commits.create(commit_id='1234',
                                                       author=self.committer1,
                                                       timestamp=time)
        self.committer2 = self.repository2.committers.create(
            participant=self.participant, userid=self.participant)
        self.commit2 = self.repository2.commits.create(commit_id='1234',
                                                       author=self.committer2,
                                                       timestamp=time)

    def test_repository(self):
        b = Branch.objects.create(latest_commit=self.commit1, name='foo')
        self.assertEqual(b.latest_commit.repository, self.repository1)

    def test_duplicate_branch(self):
        branch_name = 'foo'
        b1 = Branch.objects.create(latest_commit=self.commit1,
                                   name=branch_name)

        s = transaction.savepoint()
        with self.assertRaises(IntegrityError):
            b2 = Branch.objects.create(latest_commit=self.commit1,
                                       name=branch_name)
        transaction.savepoint_rollback(s)

        b3 = Branch.objects.get(latest_commit__repository=self.repository1,
                                name=branch_name)
        self.assertEqual(b1, b3)

    def test_branch_different_repository(self):
        branch_name = 'foo'
        b1 = Branch.objects.create(latest_commit=self.commit1,
                                   name=branch_name)
        b2 = Branch.objects.create(latest_commit=self.commit2,
                                   name=branch_name)

        self.assertNotEqual(b1, b2)

    def test_repository_branches_property(self):
        b1 = Branch.objects.create(latest_commit=self.commit1,
                                   name='foo')
        b2 = Branch.objects.create(latest_commit=self.commit2,
                                   name='foo')
        self.assertEqual(self.repository1.branches.get(name='foo'), b1)
