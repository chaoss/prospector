# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from functools import wraps
from healthmeter.utils import djcached


class cached_property(property):
    """
    A property that caches the auto-generated value after the first evaluation.
    Can be used in exactly the same way as the property() decorator in most
    cases. Setting and deleting (if possible) invalidate the cache.

    Caution must be taken when not using this as a decorator. If more than one
    property were to be defined on the same object with the getters of the same
    __name__, then a cache key collision will take place with potentially ugly
    and hard-to-debug results. If this absolutely must be done, set
    prop.cache_key to a custom value.
    """
    def __init__(self, fget, *args, **kwargs):
        assert fget is not None  # No point using cache if no getter function
        self.cache_key = fget.__name__
        super(cached_property, self).__init__(fget=fget, *args, **kwargs)

    def __get_cacheobj(self, obj):
        """Get the cached_properties dict for obj. Create if not present."""
        try:
            return obj._cached_properties

        except AttributeError:
            obj._cached_properties = {}
            return obj._cached_properties

    def __get__(self, obj, *args):
        # obj is None when accessed from the class itself
        if obj is None:
            return self

        cache = self.__get_cacheobj(obj)
        try:
            return cache[self.cache_key]

        except KeyError:
            retval = super(cached_property, self).__get__(obj, *args)
            cache[self.cache_key] = retval
            return retval

    def __set__(self, obj, value):
        # Call setter
        super(cached_property, self).__set__(obj, value)
        self.invalidate_cache(obj)

    def __delete__(self, obj):
        # Call deleter
        self.invalidate_cache(obj)

    def invalidate_cache(self, obj):
        """Invalidate the property cache"""
        try:
            del obj._cached_properties[self.cache_key]
        except (AttributeError, KeyError):
            pass

    def preseed_cache(self, obj, value):
        self.__get_cacheobj(obj)[self.cache_key] = value


project_cache_key_template = 'project:{id}:{key}'


def djcached_by_project(key, seconds):
    def keyfn(project, *args, **kwargs):
        return project_cache_key_template.format(id=project.id,
                                                 key=key)

    return djcached(keyfn, seconds)
