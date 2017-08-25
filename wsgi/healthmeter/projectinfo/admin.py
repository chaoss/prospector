# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import *

admin.site.register(Product)
admin.site.register(Release)
admin.site.register(BusinessUnit)


class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_osi_approved')
    list_editable = ('is_osi_approved',)

admin.site.register(License, LicenseAdmin)
