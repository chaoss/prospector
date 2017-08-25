# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['OPENSHIFT_APP_NAME'],
        'USER': os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME'],
        'PASSWORD': os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD'],
        'HOST': os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],
        'PORT': os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']
    }
}

MEDIA_ROOT = os.path.join(
    os.environ.get('OPENSHIFT_DATA_DIR',
                   os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '../../')),
    'media')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.environ['OPENSHIFT_PYTHON_IP'] + ':22322',
    }
}

MEDUSA_MULTITHREAD = False

EMAIL_HOST = 'smtp.corp.redhat.com'
EMAIL_PORT = 25

COMPRESS_PRECOMPILERS = (
    ('text/less',
     os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'opt', 'less',
                  'node_modules/.bin/lessc') + ' {infile}'),
)
