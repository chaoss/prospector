# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging
from healthmeter.importerutils.importers import ImporterBase

from healthmeter.btinfo.models import BugNamespace, Severity

logger = logging.getLogger(__name__)


class BugTrackerImporter(ImporterBase):
    """Generic bug tracker information importer class"""
    severity_level_map = {}
    model = BugNamespace

    @classmethod
    def resolve_importer_type(cls, bt_info):
        return bt_info.bug_tracker.bt_type.name

    def __init__(self, bt_info):
        super().__init__(bt_info)
        self.severities = {}

        for severity in Severity.objects.all():
            self.severities[severity.level] = severity

    def translate_severity(self, severity):
        """
        Convert severity string retrieved from remote bug tracker into a
        Severity object

        @arg severity String containing severity. Will be looked up in
                      self.severity_level_map to retrieve numeric level.
        @return btinfo.models.Severity object for this severity
        """
        try:
            return self.severities[self.severity_level_map[severity]]

        except KeyError:
            logger.warning("Unknown severity [%s]", severity)
            return None
