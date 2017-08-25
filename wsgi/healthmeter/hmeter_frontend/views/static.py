# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.views.generic import TemplateView


class About(TemplateView):
    template_name = 'hmeter_frontend/about.html'


class Contact(TemplateView):
    template_name = 'hmeter_frontend/contact.html'


class MigrationSchedule(TemplateView):
    template_name = 'hmeter_frontend/migration-schedule.html'
