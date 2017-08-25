# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import dateutil.parser as dparser
from django.db import transaction
import logging
import redmine
from redmine.exceptions import ResourceAttrError, ResourceNotFoundError

from healthmeter.hmeter_frontend.utils import cached_property, get_participant
from .common import BugTrackerImporter

logger = logging.getLogger(__name__)


def getresource(resource, resname, default=None):
    """
    Helper getattr()-like function that handles ResourceAttrError as well
    """
    try:
        return getattr(resource, resname, default)
    except ResourceAttrError:
        return default


class RedmineImporter(BugTrackerImporter):
    severity_level_map = {
        'Urgent': 4,
        'High': 3,
        'Immediate': 3,
        'Normal': 2,
        'Low': 1,
    }

    def __init__(self, bt_info):
        super(RedmineImporter, self).__init__(bt_info)

        bt = bt_info.bug_tracker
        self.client = redmine.Redmine(bt.baseurl,
                                      username=bt.username,
                                      password=bt.password)
        self.usercache = {}

    def getuser(self, rmuser):
        try:
            return self.usercache[rmuser.id]
        except (KeyError, AttributeError):  # Sometimes rmuser is None
            try:
                rmuser = rmuser.refresh()
            except ResourceNotFoundError:
                rmuser = None

            name = ' '.join([
                getresource(rmuser, 'firstname', ''),
                getresource(rmuser, 'lastname', '')])
            email = getresource(rmuser, 'mail', '')

            user = get_participant(name, email)

            if rmuser is not None:
                self.usercache[rmuser.id] = user

            return user

    def journal_is_closing_entry(self, journal):
        return any(detail['property'] == 'attr' and
                   detail['name'] == 'status_id' and
                   int(detail['new_value']) in self.closed_status_ids
                   for detail in journal.details)

    @cached_property
    def closed_status_ids(self):
        return set(status.id for status in self.client.issue_status.all()
                   if getresource(status, 'is_closed', False))

    @transaction.atomic
    def _run(self):
        if self.object.product:
            projects = [self.client.project.get(self.object.product)]
        else:
            projects = self.client.project.all()

        for project in projects:
            for issue in self.client.issue.all(status_id='*',
                                               project_id=project.id):
                severity = self.translate_severity(issue.priority.name)
                bug, created = self.object.bugs.get_or_create(
                    bug_id=issue.internal_id,
                    defaults={
                        'severity': self.translate_severity(
                            issue.priority.name)})

                logger.info("%s bug [%s]",
                            "Created" if created else "Found", bug)

                if not created:
                    bug.severity = severity
                    bug.save()

                else:
                    logger.info("Saving initial comment for [%s]", bug)
                    bug.comments.create(
                        comment_id='VIRTUAL-1',
                        author=self.getuser(issue.author),
                        timestamp=issue.created_on.replace(tzinfo=None))

                last_closed_time = None

                for journal in issue.journals:
                    journal_time = journal.created_on.replace(tzinfo=None)
                    comment, created = bug.comments.get_or_create(
                        comment_id=journal.id,
                        author=self.getuser(journal.user),
                        timestamp=journal_time)

                    logger.info("%s comment [%s]",
                                "Created" if created else "Found", comment)

                    if self.journal_is_closing_entry(journal):
                        last_closed_time = journal_time

                if last_closed_time is not None:
                    bug.close_date = last_closed_time
                    bug.save()


BugTrackerImporter.register_importer('redmine', RedmineImporter)
