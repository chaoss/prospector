# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.http import HttpResponse
from django.views.generic import View
import json


class RawDataView(View):
    """
    Generic Django view for outputting raw data
    """
    output = ''
    content_type = 'text/plain'

    def get_output(self):
        return self.output

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.get_output(), content_type=self.content_type)


class JsonView(RawDataView):
    """
    Generic Django view for outputting stuff via Json
    """
    data = {}
    content_type = 'application/json'

    def get_data(self):
        return self.data

    def get_output(self):
        return json.dumps(self.get_data())
