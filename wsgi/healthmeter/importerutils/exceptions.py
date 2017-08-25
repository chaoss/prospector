# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

class DuplicateImporter(Exception):
    """
    Exception raised when a duplicate importer is registered.

    Data members:
    - cls: importer base class
    - backend_name: name of duplicate backend
    """
    def __init__(self, cls, backend_name):
        super(DuplicateImporter, self).__init__(cls, backend_name)
        self.cls = cls
        self.backend_name = backend_name


class UnknownImporter(Exception):
    """
    Exception raised when an importer is attempted to be retrieved for an
    unknown backend_name.

    Data members:
    - cls: importer base class
    - backend_name: name of missing backend
    """
    def __init__(self, cls, backend_name):
        super(UnknownImporter, self).__init__(cls, backend_name)
        self.cls = cls
        self.backend_name = backend_name
