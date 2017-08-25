#!/usr/bin/env python
# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import os
from setuptools import setup

install_requires = [
    'Django==1.6',
    'psycopg2',
    'pillow',
    'django-mptt',
    'dulwich',
    'python-hglib',
    'South',
    'python-bugzilla',
    'iso8601',
    'beautifulsoup4',
    'python-dateutil',
    'feedparser',
    'python-graph-core',
    'python-magic',
    'django-colorful',
    'python-memcached',
    'jira>=0.13',
    'requests>=1.0',
    'simplejson',
    'bzr',
    'django-cachebuster',
    'jsonfield',
    # 'django-preferences>=0.0.6.1',
    'logutils',           # required for django-medusa
    'django-load',
    'suds',               # required for python-mantisbt-api
    'python-redmine',
    'launchpadlib',
    'django-compressor',
    'django-bootstrap-form',
    'django-sekizai',
    'django-activelink',
    'twython',
]

if not os.getenv('OPENSHIFT_APP_NAME'):
    install_requires.append('lxml')

# Required for django-medusa
try:
    import importlib
except ImportError:
    install_requires.append('importlib')

setup(
    name='HealthMeter',
    version='1.0',
    description='Project for assessing the health of open source projects',
    author='Chow Loong Jin',
    author_email='lchow@redhat.com',
    url='http://www.python.org/sigs/distutils-sig/',
    install_requires=install_requires
    # dependency_links=[
    #     'git+git://github.com/hyperair/django-preferences.git'
    #     '#egg=django-preferences-0.0.6.1',
    # ]
)
