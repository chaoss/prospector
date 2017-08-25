# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from .exceptions import UnknownImporter
from .registry import lookup_importer


def run_importer(instance):
    """Shortcut function to run the importer for the given instance."""
    importercls = lookup_importer(type(instance))

    with importercls.get_importer_for_object(instance) as importer:
        importer.run()
