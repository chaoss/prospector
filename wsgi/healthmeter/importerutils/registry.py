# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
import logging

from django.apps import apps
from django.utils.module_loading import import_module


logger = logging.getLogger(__name__)


ImporterEntry = collections.namedtuple('ImporterEntry', ['cls', 'key'])

importers = {}
importers_by_model = {}


def register_importer(importercls, model, key=None):
    if key is None:
        key = '{app_label}.{model_name}'.format(
            app_label=model._meta.app_label,
            model_name=model._meta.model_name)

    entry = ImporterEntry(importercls, key)
    importers[key] = entry
    importers_by_model[model] = importercls


def lookup_importer(model):
    load_importer_modules()

    if isinstance(model, str):
        model = apps.get_model(*model.split('.', 2))

    try:
        return importers_by_model[model]
    except KeyError as e:
        for key, value in importers_by_model.items():
            if key in model.__mro__:
                return value
        raise e


def get_all_importers():
    load_importer_modules()
    return importers_by_model


_importers_loaded = False


def load_importer_modules():
    """
    Import .importers for each app in INSTALLED_APPS
    """
    global _importers_loaded

    if _importers_loaded:
        return

    for app_cfg in apps.get_app_configs():
        module_name = '%s.%s' % (app_cfg.name, 'importers')

        try:
            import_module(module_name)
        except ImportError:
            logger.warning("Importing %s app importers %s module",
                           app_cfg.name, module_name)

    _importers_loaded = True
