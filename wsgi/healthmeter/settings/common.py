# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
# Django settings for healthmeter project.
import os
import sys


PROJECT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

_libdir = os.path.realpath(os.path.join(PROJECT_DIR, '..', '..', 'libs'))

for _i in ('', 'django-activelink'):
    sys.path.insert(0, os.path.join(_libdir, _i))

DEBUG = True

ADMINS = (
    ('admin', 'admin@example.com'),
)
MANAGERS = ADMINS + (
    ('manager', 'manager@example.com'),
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Singapore'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, '..', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = os.path.join(os.environ.get('BASEURL', '/'), 'static/')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, '..', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = os.path.join(os.environ.get('BASEURL', '/'), 'media/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'your secret key goes here'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                #'django.template.loaders.cached.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'healthmeter.hmeter_frontend.context_processors.feedback_form',
                'sekizai.context_processors.sekizai'
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'healthmeter.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.humanize',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'preferences',
    'healthmeter.projectinfo',
    'healthmeter.participantinfo',
    'healthmeter.vcsinfo',
    'healthmeter.mlinfo',
    'healthmeter.btinfo',
    'healthmeter.gtrendsinfo',
    'healthmeter.eventinfo',
    'healthmeter.bloginfo',
    'healthmeter.hmeter_frontend',
    'mptt',
    'colorful',
    'django_medusa',
    'django_js_reverse',
    'compressor',
    'bootstrapform',
    'sekizai',
    'activelink',
)

try:
    import django_extensions
    INSTALLED_APPS += ('django_extensions',)
except ImportError:
    pass


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s %(process)d '
                       '%(thread)d %(message)s')
        },

        'simple': {
            'format': ('[%(levelname)s %(asctime)s] %(name)s(%(process)d): '
                       '%(message)s')
        }
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },

        'console': {
            'level': 'DEBUG',
            'class': 'logutils.colorize.ColorizingStreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },

        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'healthmeter'
    }
}

ALLOWED_HOSTS = ['*']

# Django medusa settings
MEDUSA_RENDERER_CLASS = "django_medusa.renderers.DiskStaticSiteRenderer"
MEDUSA_MULTITHREAD = True
MEDUSA_DEPLOY_DIR = os.path.join(STATIC_ROOT, 'generated')

# django-js-reverse settings
JS_REVERSE_AVAILABLE_NAMESPACES = ['hmeter_frontend',
                                   'hmeter_frontend:project']

# Colour logging
from logutils.colorize import ColorizingStreamHandler
import logging
ColorizingStreamHandler.level_map[logging.INFO] = (None, '', False)

import multiprocessing
IMPORTER_CONCURRENCY = multiprocessing.cpu_count() * 2

# compressor
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile}'),
)


class __dummy_project(object):
    id = 1

COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {
    'project': __dummy_project()
}

METRIC_CACHE_LIMIT = 1  # number of days to calculate MetricCache entries for
