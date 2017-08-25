# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

def intervals(iterable):
    prev_value = None
    for x in iterable:
        if prev_value is not None:
            yield x - prev_value
        prev_value = x


def filternone(iterable):
    return (i for i in iterable if i is not None)


def uniq(iterable, key=None):
    if key is None:
        key = lambda x: x

    prev_key = float('nan')
    for i in iterable:
        current_key = key(i)
        if current_key != prev_key:
            yield i
            prev_key = current_key
