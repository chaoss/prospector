# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.exceptions import ImproperlyConfigured
from itertools import chain, repeat
from .models import Project
from .resources import register_resource

# See deprecation
# https://docs.djangoproject.com/en/1.11/ref/models/meta/#migrating-from-the-old-api

def get_fields_with_model(cls):
    return [
        (f, f.model if f.model != cls else None)
        for f in cls._meta.get_fields()
        if not f.is_relation
        or f.one_to_one
        or (f.many_to_one and f.related_model)
    ]


def get_m2m_with_model(cls):
    return [
        (f, f.model if f.model != cls else None)
        for f in cls._meta.get_fields()
        if f.many_to_many and not f.auto_created
    ]


@classmethod
def _get_project_field(cls):
    """
    Returns (project_field_name, is_m2m) tuple
    """
    try:
        return cls._project_field_cache

    except AttributeError:
        fields_iter = chain(
            zip(repeat(False), get_fields_with_model(cls)),
            zip(repeat(True), get_m2m_with_model(cls))
        )

        # Look for fk/1to1 field
        for m2m, (field, model) in fields_iter:
            if field.rel and field.rel.to is Project:
                if model is None:
                    model = cls

                model._project_field_cache = (field.name, m2m)
                return model._project_field_cache

        raise ImproperlyConfigured("No foreign key pointing to Project "
                                   "on {0}.{1}".format(
                                       cls._meta.app_label,
                                       cls._meta.model_name))


def _get_projects(self):
    """
    Gets project(s) associated with this resource.
    """
    project_attr, is_m2m = self.get_project_field()

    if not is_m2m:
        return [getattr(self, project_attr)]

    else:
        return getattr(self, project_attr).all()


def resource(model):
    """Decorator for resource classes"""
    model.get_project_field = _get_project_field
    model.get_projects = _get_projects

    register_resource(model)

    return model
