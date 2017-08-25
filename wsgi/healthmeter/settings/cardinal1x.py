# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'healthmeter1x',
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
        'KEY_PREFIX': 'stable1x'
    }
}

DEBUG = False
