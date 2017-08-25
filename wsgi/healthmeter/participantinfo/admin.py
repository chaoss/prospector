# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from .models import *
from django.contrib import admin

for model in (Participant, EmailAddress, EmailDomain):
    admin.site.register(model)
