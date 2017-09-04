# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import *
from healthmeter.btinfo.models import BugNamespace
from healthmeter.bloginfo.models import Blog
from healthmeter.eventinfo.models import Event
from healthmeter.mlinfo.models import MailingList, MailingListProject
from healthmeter.projectinfo.models import Release, License
from healthmeter.vcsinfo.models import Repository

for model in (Blog, Event,
              MetricScoreConstants,
              Repository, MailingList, MailingListProject,
              BugNamespace):
    admin.site.register(model)


def make_inline(model_, extra_=0):
    class Inline(admin.StackedInline):
        model = model_
        extra = extra_

    return Inline


class MetricAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    inlines = [make_inline(Metric)]
    list_display = ('title', 'weight', 'algorithm')

admin.site.register(Metric, MetricAdmin)


class BugNamespaceInline(admin.StackedInline):
    verbose_name = "Bug Namespace-Project Relationships"
    verbose_name_plural = "Bug Namespace-Project Relationships"
    model = BugNamespace.projects.through
    extra = 0


class ProjectInline(admin.StackedInline):
    verbose_name = "Subproject"
    verbose_name_plural = "Subprojects"
    model = Project
    extra = 0


class ProjectAdmin(MPTTModelAdmin):
    inlines = [ProjectInline,
               make_inline(Release),
               make_inline(Repository),
               BugNamespaceInline,
               make_inline(Event),
               make_inline(MailingListProject)]
    mptt_level_indent = 20
    filter_horizontal = ['licenses']
    list_display = ('name', 'business_unit', 'is_wip')
    list_filter = ('business_unit', 'is_wip')

admin.site.register(Project, ProjectAdmin)
