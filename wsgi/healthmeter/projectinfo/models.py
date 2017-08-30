# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models
from django.utils.text import slugify
from itertools import chain, repeat
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
import os
from healthmeter.managers import get_natural_key_manager


class BusinessUnit(models.Model):
    name = models.CharField(max_length=255, unique=True)

    objects = get_natural_key_manager('name')

    def __str__(self):
        return self.name

    @property
    def root_projects(self):
        return self.projects.filter(parent__isnull=True)


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(blank=True, default='')
    business_unit = models.ForeignKey(BusinessUnit, related_name='products')

    objects = get_natural_key_manager('name')

    def __str__(self):
        return self.name


class Project(MPTTModel):
    name = models.CharField(max_length=255)
    website_url = models.URLField(blank=True, null=True)

    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    governance = models.TextField(default="", blank=True)
    licenses = models.ManyToManyField('License', related_name='projects',
                                      null=True, blank=True)
    description = models.TextField(default="", blank=True)
    has_contributor_agreement = models.BooleanField(default=False)

    business_unit = models.ForeignKey(BusinessUnit,
                                      blank=True, null=True,
                                      related_name='projects')

    start_date = models.DateField(blank=True, null=True)

    is_wip = models.BooleanField(null=False, default=True,
                                 verbose_name="Configuration in progress")

    def __logo_path(self, filename):
        return os.path.join(
            'projectinfo/logos',
            str(self.id) if self.id else slugify(self.name))

    logo = models.ImageField(null=True, blank=True,
                             upload_to=__logo_path)

    tree = TreeManager()

    def __str__(self):
        return str(self.name)

    class MPTTMeta:
        order_insertion_by = ['name']


class Release(models.Model):
    project = models.ForeignKey(Project, related_name='releases')
    version = models.CharField(max_length=100)
    date = models.DateField()

    objects = get_natural_key_manager('project', 'version')

    def __str__(self):
        return "{0} {1}{2}".format(
            self.project.name,
            '' if self.version.startswith('v') else 'v',
            self.version)

    class Meta:
        unique_together = ('project', 'version')
        ordering = ('date', 'version')


class License(models.Model):
    name = models.TextField(unique=True)
    is_osi_approved = models.BooleanField()

    objects = get_natural_key_manager('name')

    def __str__(self):
        return self.name
