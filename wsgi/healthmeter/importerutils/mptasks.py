# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
Small collection of callable classes for helping out with multiprocessing
"""
import logging
from .shortcuts import run_importer

logger = logging.getLogger(__name__)


class ImporterTask:
    def __init__(self, obj):
        self.obj = obj

    def __call__(self):
        try:
            run_importer(self.obj)

        except:
            logger.error("Importer for [%s] failed", self.obj, exc_info=True)
