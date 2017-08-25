# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import os


def splitext_full(filename):
    """
    Extracts full extension from filename. e.g. foo.tar.gz -> tar.gz. Supports
    up to 2 extension components.

    @arg filename File name to parse
    @return Parsed extension
    """
    filename2, ext1 = os.path.splitext(filename)
    _, ext2 = os.path.splitext(filename2)

    if ext2:
        return ext2 + ext1

    else:
        return ext1


__all__ = ['splitext_full']
