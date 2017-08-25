# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

#!/usr/bin/python

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'healthmeter.settings'
sys.path.insert(0, '/home/hyperair/src/healthmeter/wsgi')

from healthmeter.hmeter_frontend.metrics import algorithms
from healthmeter.hmeter_frontend.models import Project

for p in Project.objects.root_nodes():
    for i in algorithms.values():
        print("{0}: {1}".format(i.__name__, i(p).normalized_score))
