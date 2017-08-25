# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

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
        'KEY_PREFIX': 'staging'
    }
}

DEBUG = False

MEDUSA_URL_PREFIX = '/staging/'
STATIC_URL = '/staging/static/'
MEDIA_URL = '/staging/media/'

EMAIL_HOST = 'smtp.corp.redhat.com'
EMAIL_PORT = 25
