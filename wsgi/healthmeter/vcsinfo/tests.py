# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
Tests for the vcsinfo app
"""
import datetime

from django.db import IntegrityError
from django.test import TestCase

from .models import *


class TestType(TestCase):
    def test_unique(self):
        Type.objects.get(name='git')

        with self.assertRaises(IntegrityError):
            Type.objects.create(name='git')

    def test_str(self):
        t = Type.objects.get(name='git')
        self.assertEqual(t, 'git')


class TestRepository(TestCase):
    def test_duplicate(self):
        t = Type.objects.get(name='git')
        url = 'git://foo/bar.git'

        Repository.objects.create(type=t, url=url)

        with self.assertRaises(IntegrityError):
            Repository.objects.create(type=t, url=url)

    def test_str(self):
        t = Type.objects.get(name='git')
        url = 'git://foob/bar.git'
        r = Repository.objects.create(type=t, url=url)

        self.assertEqual(r, url)


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
