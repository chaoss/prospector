# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

def coerce_unicode(string):
    """
    Anti-boilerplate function that coerces a string object into a unicode
    object. Does nothing if string is unicode to begin with.
    """
    if isinstance(string, str):
        return str(string)

    # Assume string is a str (or pretending to be) instead
    return string.decode('utf8', 'replace')


__all__ = [
    'coerce_unicode'
]
