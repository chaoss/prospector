# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.test import TestCase
from django.db import IntegrityError

from .models import *


class TestProject(TestCase):
    """Test case that contains tests for Project model"""
    def test_duplicate(self):
        """Tests that multiple projects with the same name can exist"""
        p1 = Project.objects.create(name='test')
        p2 = Project.objects.create(name='test')

        self.assertNotEqual(p1, p2)

    def test_tree(self):
        """Tests MPTT tree structure of Project"""
        p1 = Project.objects.create(name='test')
        p2 = p1.children.create(name='test')

        self.assertEqual(p2.parent, p1)
        self.assertIn(p2, p1.children.all())

    def test_unicode(self):
        """Tests the __unicode__ function"""
        p1 = Project(name='test')
        self.assertEqual(unicode(p1), 'test')


class TestRelease(TestCase):
    """Test case that contains tests for Release model"""
    def test_unique(self):
        """Tests that Release is unique per version per project"""
        p = Project.objects.create(name='test')
        r = p.releases.create(version='1.0', date=datetime.date.today())

        with self.assertRaises(IntegrityError):
            p.releases.create(version='1.0',
                              date=(datetime.date.today() -
                                    datetime.timedelta(days=1)))

    def test_ordering(self):
        """
        Tests that the ordering of project releases is by date followed by
        version
        """
        p = Project.objects.create(name='test')
        r1 = p.releases.create(version='2.0', date=datetime.date.today())
        r2 = p.releases.create(version='1.0', date=datetime.date.today())
        r3 = p.releases.create(version='3.0',
                               date=(datetime.date.today() -
                                     datetime.timedelta(days=1)))

        releases = p.releases.all()
        self.assertEqual(releases[0], r3)
        self.assertEqual(releases[1], r2)
        self.assertEqual(releases[2], r1)
