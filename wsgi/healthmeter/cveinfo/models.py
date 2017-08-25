# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
import re

from healthmeter.managers import get_natural_key_manager
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.decorators import resource
from mptt.models import TreeForeignKey


@resource
class Product(models.Model):
    vendor = models.CharField(max_length=100, default=None)
    product = models.CharField(max_length=100, default=None)

    project = TreeForeignKey(Project, related_name='cpeproducts')

    objects = get_natural_key_manager('vendor', 'product')

    class Meta:
        unique_together = ('vendor', 'product')

    def __unicode__(self):
        return u'cpe:/a:%s:%s' % (self.vendor, self.product)


class CVE(models.Model):
    products = models.ManyToManyField(Product, related_name='cves')

    year = models.IntegerField()
    number = models.IntegerField()

    published_datetime = models.DateTimeField()

    objects = get_natural_key_manager('year', 'number')

    class Meta:
        unique_together = ('year', 'number')

    def __unicode__(self):
        return u'CVE-%04d-%04d' % (self.year, self.number)
