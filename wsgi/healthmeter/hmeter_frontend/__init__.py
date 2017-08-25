# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# HACK: Import models, and then import metrics.algorithms here to ensure that
# the algorithms are populated.
from . import models
from .metrics import algorithms
from . import handlers
