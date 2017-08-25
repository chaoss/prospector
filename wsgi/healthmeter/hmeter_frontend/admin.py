# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from preferences.admin import PreferencesAdmin

from .models import *
from healthmeter.btinfo.models import BugNamespace
from healthmeter.bloginfo.models import Blog
from healthmeter.microbloginfo.models import Microblog
from healthmeter.cveinfo.models import Product as CPEProduct
from healthmeter.eventinfo.models import Event
from healthmeter.jamiqinfo.models import Topic
from healthmeter.gtrendsinfo.models import Query as GTrendsQuery
from healthmeter.ircinfo.models import (Server as IrcServer,
                                        Channel as IrcChannel)
from healthmeter.mlinfo.models import MailingList, MailingListProject
from healthmeter.projectinfo.models import Release, License
from healthmeter.vcsinfo.models import Repository
from healthmeter.downloadinfo.models import DataSource as DownloadSource

for model in (IrcServer, IrcChannel, Blog, Microblog, Event,
              CPEProduct, MetricScoreConstants,
              Repository, MailingList, MailingListProject,
              BugNamespace, Topic.projects.through, DownloadSource):
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


class CPEProductInline(admin.StackedInline):
    verbose_name = "CPE Product"
    verbose_name_plural = "CPE Products"
    model = CPEProduct
    extra = 0


class IrcChannelInline(admin.StackedInline):
    verbose_name = "IRC Channel-Project Relationship"
    verbose_name_plural = "IRC Channel-Project Relationships"
    model = IrcChannel.projects.through
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
               CPEProductInline,
               make_inline(Event),
               make_inline(MailingListProject),
               make_inline(Blog.projects.through),
               make_inline(Microblog.projects.through),
               make_inline(DownloadSource),
               make_inline(GTrendsQuery),
               IrcChannelInline]
    mptt_level_indent = 20
    filter_horizontal = ['licenses']
    list_display = ('name', 'business_unit', 'is_wip')
    list_filter = ('business_unit', 'is_wip')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Options, PreferencesAdmin)
