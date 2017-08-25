# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""Common functions for mailing list importers"""
import os


def get_mailing_list_path(mailing_list):
    """Returns a path to the mailing list data directory"""
    path = os.path.join(os.getenv('OPENSHIFT_DATA_DIR',
                                  os.getenv('TMPDIR', '/tmp')),
                        'mailing-lists', str(mailing_list.pk))

    if not os.path.isdir(path):
        os.makedirs(path)

    return path
