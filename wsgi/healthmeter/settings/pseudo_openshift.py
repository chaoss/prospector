# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- python -*-

from .common import LOGGING

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'healthmeter',
        'USER': 'healthmeter',
        'PASSWORD': 'healthmeter',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
        'KEY_PREFIX': 'healthmeterdev'
    }
}

LOGGING['handlers']['console']['level'] = 'INFO'
