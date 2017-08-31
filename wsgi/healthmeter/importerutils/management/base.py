# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import abc
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.db.models import FieldDoesNotExist
import itertools
import logging
import multiprocessing

from healthmeter.importerutils.mptasks import ImporterTask

logger = logging.getLogger(__name__)


class ImporterCommand(BaseCommand):
    __metaclass__ = abc.ABCMeta
    args = '[<id>...]'
    help_template = """
Run the {importer_type} importer for the id's provided. If no id's are
provided, it is run on all entries in the database.

<id> Refers to the id of each {model_type} instance.
"""
    max_concurrency = getattr(settings, 'IMPORTER_CONCURRENCY',
                              multiprocessing.cpu_count() * 2)

    @abc.abstractproperty
    def model(self):
        """Model class for which the IDs belong to"""
        pass

    @abc.abstractproperty
    def importer(self):
        """Importer class"""
        pass

    @property
    def importer_type(self):
        """String containing the importer name"""
        return self.importer.__name__

    @property
    def model_type(self):
        """String containing the importer model name"""
        return self.model.__name__

    @property
    def help(self):
        return self.help_template.format(
            importer_type=self.importer_type,
            model_type=self.model_type)

    def get_queryset(self, args):
        qs = (self.model.objects.filter(id__in=args)
              if args
              else self.model.objects.all())

        try:
            self.model._meta.get_field('last_updated')
            qs = itertools.chain(qs.filter(last_updated=None),
                                 qs.order_by('last_updated'))

        except FieldDoesNotExist:
            pass

        return qs

    def handle(self, *args, **options):
        # Get all objects..
        objects = list(self.get_queryset(args))

        # ..and close DB connection before we spawn the pool
        connection.close()

        pool = multiprocessing.Pool(self.max_concurrency)
        results = [pool.apply_async(ImporterTask(obj))
                   for obj in objects]

        for promise in results:
            try:
                # Workaround for multiprocessing hanging bug -- specify a large
                # timeout to be more or less equivalent to promise.get()
                # See: https://stackoverflow.com/questions/1408356/
                promise.get(365*24*3600)
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    logger.warning("Importer terminated by keyboard interrupt")
                    pool.terminate()
                    pool.join()
                    raise

                logger.error("Couldn't import %s from %s. Skipping..",
                             obj, self.importer, exc_info=True)
