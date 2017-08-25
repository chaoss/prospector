# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import os

from .common import *

ON_OPENSHIFT = 'OPENSHIFT_REPO_DIR' in os.environ
if ON_OPENSHIFT:
    from .openshift import *

try:
    from .local import *
except ImportError:
    pass
