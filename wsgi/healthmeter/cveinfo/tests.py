# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from .models import *


class TestProduct(TransactionTestCase):
    def test_unique(self):
        Product.objects.create(product='product', vendor='vendor')

        with self.assertRaises(IntegrityError):
            Product.objects.create(product='product', vendor='vendor')

    def test_missingfields(self):
        with self.assertRaises(IntegrityError):
            sid = transaction.savepoint()
            Product.objects.create(product='product')

        transaction.savepoint_rollback(sid)

        with self.assertRaises(IntegrityError):
            Product.objects.create(vendor='vendor')


class TestCVE(TestCase):
    @staticmethod
    def _get_product():
        return Product.objects.create(product='product', vendor='vendor')

    def test_unique(self):
        now = datetime.datetime.utcnow()
        product = self._get_product()
        product.cves.create(year=2012, number=1, published_datetime=now)

        with self.assertRaises(IntegrityError):
            CVE.objects.create(year=2012, number=1, published_datetime=now)

    def test_unicode(self):
        now = datetime.datetime.utcnow()

        cve = CVE(year=2012, number=1, published_datetime=now)
        cve.save()

        self.assertEqual(unicode(cve), 'CVE-2012-0001')

    def test_missingfields(self):
        now = datetime.datetime.utcnow()
        kwargs = {
            'year': 2012,
            'number': 1,
            'published_datetime': now
        }
        required_fields = kwargs.keys()

        for field in required_fields:
            kwargs2 = kwargs.copy()
            del kwargs2[field]

            with self.assertRaises(IntegrityError):
                sid = transaction.savepoint()
                CVE.objects.create(**kwargs2)

            transaction.savepoint_rollback(sid)
