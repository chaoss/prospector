# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.conf.urls import include, url, static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

import django_js_reverse.views

import healthmeter.hmeter_frontend.urls
from healthmeter.views.errors import PageNotFoundView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^jsreverse/', django_js_reverse.views.urls_js,
        name='js_reverse'),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL,
                                 document_root=settings.MEDIA_ROOT)

urlpatterns += [
    url(r'', include(healthmeter.hmeter_frontend.urls,
                     namespace="hmeter_frontend")),
]

handler404 = PageNotFoundView.as_view()
