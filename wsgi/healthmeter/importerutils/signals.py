# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import django.dispatch

import_finished = django.dispatch.Signal(providing_args=['start', 'end',
                                                         'importer'])
