# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from functools import wraps

from django.db import transaction
from django.core.cache import cache
import itertools

import types


def djcached(key_or_keyfn, seconds):
    """
    Decorator factory that makes the function cached for `seconds' using
    `key_or_keyfn`. If `key_or_keyfn` is callable, it is called using the
    received arguments to derive a key. Otherwise, it is treated as the cache
    key.

    Usage:
    @djcached("foo", 1 * 60 * 60)  # Cache using key "foo" for 1 hour
    def foo():
        pass

    @djcached(lambda arg: arg.id, 1 * 60 * 60)  # Derive key from argument
    def foo(arg):
        pass
    """
    def decorator(fn):
        def do_cache_call(key, *args, **kwargs):
            recache = kwargs.pop('_djcached_force_recache', False)
            retval = (None if recache else cache.get(key))
            if retval is not None:
                return retval

            retval = fn(*args, **kwargs)
            cache.set(key, retval, seconds)
            return retval

        if callable(key_or_keyfn):  # Treat as keyfn
            keyfn = key_or_keyfn

            @wraps(fn)
            def wrapper(*args, **kwargs):
                recache = kwargs.pop('_djcached_force_recache', False)
                key = keyfn(*args, **kwargs)

                return do_cache_call(key, *args,
                                     _djcached_force_recache=recache,
                                     **kwargs)

        else:
            key = key_or_keyfn

            @wraps(fn)
            def wrapper(*args, **kwargs):
                return do_cache_call(key, *args, **kwargs)
        return wrapper
    return decorator


class abstractclassmethod(classmethod):
    """
    A decorator indicating abstract classmethods.

    Similar to abstractmethod.

    Usage:

        class C(metaclass=ABCMeta):
            @abstractclassmethod
            def my_abstract_classmethod(cls, ...):
                ...

    'abstractclassmethod' is deprecated. Use 'classmethod' with
    'abstractmethod' instead.
    """

    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


def pairwise(iterable):
    """
    iterable helper that allows for getting pairs of elements. First pair and
    last element is padded with None.

    Example:
    pairwise([0,1,2,3]) -> ((None, 0), (0,1), (1,2), (2,3))
    """
    a, b = itertools.tee(iterable)
    a = itertools.chain((None,), a)
    b = itertools.chain(b, (None,))
    return itertools.izip(a, b)


class ProxyObject(object):
    """Proxy object that allows for overriding some properties"""
    __origobj = None            # Hack to avoid getattr recursion when pickling

    def __init__(self, obj, **kwargs):
        self.__dict__.update(kwargs)
        self.__origobj = obj

    def __getattr__(self, attr):
        return getattr(self.__origobj, attr)

    def __repr__(self):
        args = [repr(self.__origobj)]
        args.extend(
            '{0}={1}'.format(str(key), repr(value))
            for key, value in self.__dict__.iteritems()
            if key != '_ProxyObject__origobj'
        )

        return 'ProxyObject({0})'.format(', '.join(args))
