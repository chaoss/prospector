# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from healthmeter.views.generic import JsonView
from healthmeter.hmeter_frontend.forms import FeedbackForm
import json


class FeedbackView(View):
    @classmethod
    def as_view(cls, *args, **kwargs):
        return csrf_exempt(super(FeedbackView, cls).as_view(*args, **kwargs))

    @staticmethod
    def format_email(name, email):
        return '{0} <{1}>'.format(name, email)

    def post(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST)

        if not form.is_valid():
            respdata = {
                'status': 'fail',
                'errors': form.errors
            }
            responsecls = HttpResponseBadRequest

        else:
            respdata = {
                'status': 'ok',
                'errors': {}
            }
            responsecls = HttpResponse
            recipients = [self.format_email(name, email)
                          for name, email in settings.MANAGERS]

            message = '{0}\n-- \nSent from: {1}\n'.format(
                form.cleaned_data['message'],
                request.META['HTTP_REFERER'])

            send_mail(subject='[OSP feedback] ' + form.cleaned_data['subject'],
                      message=message,
                      from_email=self.format_email(
                          form.cleaned_data['name'],
                          form.cleaned_data['email']),
                      recipient_list=recipients)

        return responsecls(json.dumps(respdata),
                           content_type='application/json')
