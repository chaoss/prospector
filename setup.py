#!/usr/bin/env python
# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import os
from setuptools import setup

install_requires = [
    'Django>=1.11',
    'psycopg2',
    'pillow',
    'beautifulsoup4',
    'python-dateutil',
    'python-graph-core',
    'python-magic',
    'python-memcached',
    'jsonfield',
    'logutils',           # required for django-medusa
    'django-load',
    'django-compressor',
    'django-bootstrap-form',
    'django-sekizai',
    'django-mptt',
    'django-medusa',
    'django-js-reverse',
    'twython',
    'perceval'
]

# Hack for installing Django package before
# some dependent packages
setup_requires = [
    'django-colorful',
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
