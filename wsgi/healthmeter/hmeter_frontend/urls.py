# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.conf.urls import include, patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from . import views

project_urlpatterns = patterns(
    '',
    url(r'^$', views.project.ProjectIndex.as_view(), name="index"),

    url(r'^\+problems$', views.project.ProblematicProjects.as_view(),
        name="problems"),

    url(r'^\+compare/(?P<ids>([0-9]+,)+[0-9]+)$',
        views.project.CompareProject.as_view(),
        name="compare"),

    url(r'^(?P<pk>\d+)/$', views.project.ProjectDetail.as_view(),
        name="detail"),

    url(r'^(?P<id>\d+)/commits/(?P<domain>.*)$',
        views.project.CommitDataView.as_view(),
        name="commitdata"),

    url(r'^(?P<id>\d+)/committers/(?P<domain>.*)$',
        views.project.CommitterDataView.as_view(),
        name="committerdata"),

    url(r'^(?P<id>\d+)/emails/(?P<domain>.*)$',
        views.project.MailingListDataView.as_view(),
        name="mldata"),

    url(r'^(?P<id>\d+)/emailers/(?P<domain>.*)$',
        views.project.MailingListPosterDataView.as_view(),
        name="mlposterdata"),

    url(r'^(?P<id>\d+)/bugs/(?P<domain>.*)$',
        views.project.BugDataView.as_view(),
        name="btdata"),

    url(r'^(?P<id>\d+)/bugreporters/(?P<domain>.*)$',
        views.project.BugReporterDataView.as_view(),
        name="btreporterdata"),

    url(r'^(?P<id>\d+)/irc/$', views.project.IrcDataView.as_view(),
        name="ircdata"),

    url(r'^(?P<id>\d+)/blogs/$', views.project.BlogDataView.as_view(),
        name="blogdata"),

    url(r'^(?P<id>\d+)/microblogs/$',
        views.project.MicroblogDataView.as_view(),
        name="microblogdata"),

    url(r'^(?P<id>\d+)/events/$', views.project.EventDataView.as_view(),
        name="eventdata"),

    url(r'^(?P<id>\d+)/gtrends/$', views.project.GTrendsDataView.as_view(),
        name="gtrendsdata"),

    url(r'^(?P<id>\d+)/jamiq/$', views.project.JamiqDataView.as_view(),
        name="jamiqdata"),

    url(r'(?P<id>\d+)/metric/$', views.project.MetricDataView.as_view(),
        name="metricdata"),

    url(r'(?P<pk>\d+)/metrichistory/$',
        views.project.MetricHistoryView.as_view(),
        name="metrichistory"),
)

urlpatterns = patterns(
    '',
    url(r'^$',
        RedirectView.as_view(
            url=reverse_lazy('hmeter_frontend:project:index'),
            permanent=True
        )),

    url(r'^about$', views.static.About.as_view(),
        name='about'),

    url(r'^contact$', views.static.Contact.as_view(),
        name='contact'),

    url(r'^feedback$', views.feedback.FeedbackView.as_view(),
        name='feedback'),

    url(r'^project/', include(project_urlpatterns,
                              namespace='project')),

    url(r'^business-units/', views.business_units.BusinessUnitIndex.as_view(),
        name='business_units'),

    url(r'^all-projects/', views.all_projects.AllProjectsView.as_view(),
        name='all_projects'),
)
