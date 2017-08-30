# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
from django.db import models
import mptt.managers


class QuerySetManager(models.Manager):
    """
    A Manager class that can be assigned to objects supporting the model's
    nested QuerySet.

    Usage:
    class Model:
        objects = QuerySetManager(Model)

        class QuerySet(models.query.QuerySet):
            ...
    """
    def get_queryset(self):
        return self.model.QuerySet(self.model)

    def __getattr__(self, name, *args):
        if name.startswith('_'):
            raise AttributeError

        return getattr(self.get_queryset(), name, *args)


class ProxyTreeManager(mptt.managers.TreeManager):
    """
    Custom Manager class that makes proxy classes with MPTT feasible by setting
    the model of the queryset back to the derived class.

    This makes the TreeManager methods which query things return instances
    constructed with the proxy model instead of the base model.
    """

    def _mptt_filter(self, *args, **kwargs):
        qs = super(ProxyTreeManager, self)._mptt_filter(*args, **kwargs)
        qs.model = self.model
        return qs


class NaturalKeyManagerBase(models.Manager):
    """
    Base class for a custom Manager that simplifies natural key handling. This
    manager adds a .natural_key() method to the model it is added to, and
    proivdes a .get_by_natural_key() method for queryng instances of the model
    via the natural key.

    You should not construct this class directly, but instead derive from it
    and set natural_key_columns to a list of field names to use for generating
    the natural key.
    """
    # Override in specific NaturalKeyManager derivative classes
    natural_key_columns = []
    FieldInfo = collections.namedtuple('fieldinfo',
                                       ['field', 'model', 'direct', 'm2m'])

    def contribute_to_class(self, model, name):
        super(NaturalKeyManagerBase, self).contribute_to_class(model, name)
        model.natural_key = lambda self_: self._get_natural_key(self_)

    def _get_field_info(self, fieldname):
        return self.FieldInfo(*self.model._meta.get_field_by_name(fieldname))

    def _get_natural_key(self, model_instance):
        def gen():
            for col in self.natural_key_columns:
                fieldinfo = self._get_field_info(col)
                rel = getattr(fieldinfo.field, 'rel', None)

                if getattr(fieldinfo.field, 'rel', None) is None:
                    yield getattr(model_instance, col)
                    continue

                # .rel is not None, so this is a foreign object
                if fieldinfo.m2m:
                    # m2m
                    yield [obj.natural_key()
                           for obj in getattr(model_instance, col).all()]
                else:
                    # *toOne relation
                    yield getattr(model_instance, col).natural_key()

        return tuple(gen())

    def get_by_natural_key(self, *args):
        query = models.Q()

        for col, value in zip(self.natural_key_columns, args):
            fieldinfo = self._get_field_info(col)
            if not fieldinfo.direct:
                raise ConfigurationError("Cannot use NaturalKeyManager "
                                         "with indirect fields.")

            if getattr(fieldinfo.field, 'rel', None) is None:
                # Not a foreign object
                query &= models.Q(**{col: value})

            else:
                # some sort of foreign relation
                foreign_mgr = fieldinfo.field.rel.to._default_manager

                if fieldinfo.m2m:
                    # m2m relation
                    for obj in foreign_mgr.get_by_natural_key(*value):
                        query &= models.Q(**{col: obj})

                else:
                    # toOne foreign relation
                    query &= models.Q(
                        **{col: foreign_mgr.get_by_natural_key(*value)})

        return self.get(query)


def get_natural_key_manager(*cols):
    class NaturalKeyManager(NaturalKeyManagerBase):
        natural_key_columns = cols

    return NaturalKeyManager()
