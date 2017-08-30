# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import abc
import datetime
import logging
from healthmeter.utils import abstractclassmethod
import six

from .exceptions import UnknownImporter, DuplicateImporter
from .registry import register_importer
from .signals import import_finished

logger = logging.getLogger(__name__)


class ImporterBaseMeta(abc.ABCMeta):
    def __new__(cls, name, bases, attrs):
        instance = super().__new__(cls, name, bases, attrs)
        try:
            model = attrs['model']
            logger.debug("Registering importer %s for model %s", instance,
                         model)
            register_importer(instance, model)
        except KeyError:
            pass

        return instance


@six.add_metaclass(ImporterBaseMeta)
class ImporterBase(object):
    """
    Abstract importer class to define a common interface for importing
    things
    """
    def __init__(self, obj):
        self.object = obj
        self.earliest_point = datetime.datetime.utcnow()
        self.latest_point = None

    def close(self):
        """
        Free resources for the importer. This function is a stub and should
        be overridden as necessary.
        """
        pass

    # __enter__ and __exit__ functions for `with' syntax
    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        self.close()

    def set_last_updated(self, time=None):
        """
        Sets the last_updated field of the object being imported to time.

        @arg time datetime object representing what last_updated should be set
                  to. Defaults to datetime.utcnow()
        """

        if not hasattr(self.object, 'last_updated'):
            return

        last_updated = datetime.datetime.utcnow() if time is None else time

        if self.object.last_updated != last_updated:
            logger.info("Setting last_updated on %s to %s",
                        self.object, last_updated)

            self.object.last_updated = last_updated
            self.object.save()

    def record_timestamp(self, dt):
        """
        Function to help keep track of the earliest point imported in this
        round.
        """
        dt = (datetime.datetime.combine(dt, datetime.time())
              if isinstance(dt, datetime.date)
              else dt)
        self.earliest_point = min(dt, self.earliest_point)
        self.latest_point = (dt if self.latest_point is None
                             else max(dt, self.latest_point))

    @abc.abstractmethod
    def _run(self):
        """Abstract method to be overridden for importer implementation"""
        pass

    def run(self):
        """Run the importer"""
        self._run()
        self.set_last_updated()
        import_finished.send_robust(type(self),
                                    start=self.earliest_point,
                                    end=self.latest_point,
                                    importer=self)

    @classmethod
    def register_importer(cls, backend_name, importer_class):
        """Register an importer with this backend_name"""
        if not hasattr(cls, '_importers'):
            cls._importers = {}

        if backend_name in cls._importers:
            raise DuplicateImporter(cls, backend_name)

        cls._importers[backend_name] = importer_class

    @classmethod
    def get_importer(cls, backend_name):
        """Retrieve a constructed importer for backend_name"""
        try:
            return cls._importers[backend_name]

        except (KeyError, AttributeError):
            raise UnknownImporter(cls, backend_name)

    @classmethod
    def get_importer_for_object(cls, obj):
        """
        Get importer used to import this object. See .get_importer().

        @returns Constructed importer instance for obj
        """
        return cls.get_importer(cls.resolve_importer_type(obj))(obj)

    @abstractclassmethod
    def resolve_importer_type(cls, obj):
        """Resolve the key for get_importer"""
        pass
