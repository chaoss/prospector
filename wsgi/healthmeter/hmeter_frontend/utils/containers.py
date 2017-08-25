# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setattr__


def filterdict(d, blacklist=None, whitelist=None):
    """
    Create a new dict with keys either present in blacklist or not present in
    whitelist filtered out.
    """
    keys = set(d.iterkeys())
    if whitelist is not None:
        keys &= set(whitelist)

    if blacklist is not None:
        keys ^= set(blacklist)

    return dict((k, v) for k, v in d.iteritems() if k in keys)
