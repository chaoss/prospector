# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.exceptions import ImproperlyConfigured
from itertools import chain, izip, repeat
from .models import Project
from .resources import register_resource


@classmethod
def _get_project_field(cls):
    """
    Returns (project_field_name, is_m2m) tuple
    """
    try:
        return cls._project_field_cache

    except AttributeError:
        fields_iter = chain(
            izip(repeat(False), cls._meta.get_fields_with_model()),
            izip(repeat(True), cls._meta.get_m2m_with_model())
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
