# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from .iterators import filternone


def weighted_average(iterable):
    """
    Calculates a weighted average of the (value, weight) tuples in
    iterable.

    @arg iterable that yields (value, weight) tuples
    @return weighted average of values
    """
    numerator = 0
    denominator = 0
    for value, weight in iterable:
        numerator += value * weight
        denominator += weight

    return float(numerator) / denominator


def __or_none_helper(fn, *args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        iterable = args[0]
    else:
        iterable = args

    try:
        return fn(filternone(iterable))
    except ValueError:
        return None


def max_or_none(*args):
    """
    Proxy for max() that allows for empty iterable to be passed.
    """
    return __or_none_helper(max, *args)


def min_or_none(*args):
    return __or_none_helper(min, *args)
