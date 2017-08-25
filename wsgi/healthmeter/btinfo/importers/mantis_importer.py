# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import transaction
from itertools import chain
import logging
from mantisbt.client import MantisClient
from suds.client import WebFault
import dateutil.tz as dtz
import os

from healthmeter.hmeter_frontend.utils.mail import get_participant
from healthmeter.hmeter_frontend.utils.misc import coerce_unicode
from .common import BugTrackerImporter

logger = logging.getLogger(__name__)


class MantisImporter(BugTrackerImporter):
    severity_level_map = {
        'feature': 1,
        'trivial': 1,
        'tweak': 1,
        'minor': 2,
        'major': 3,
        'crash': 4,
        'block': 4
    }

    def __init__(self, bt_info):
        super(MantisImporter, self).__init__(bt_info)
        soapurl = os.path.join(bt_info.bug_tracker.baseurl,
                               'api/soap/mantisconnect.php?wsdl')

        self.client = MantisClient(bt_info.bug_tracker.username,
                                   bt_info.bug_tracker.password,
                                   soapurl)

        projectlist = self.client.get_users_projects()

        if self.object.product:
            self.projects = [project for project in projectlist
                             if project.name == self.object.product]
        else:
            self.projects = projectlist

    @staticmethod
    def sanitize_datetime(dt):
        if dt.tzinfo is None:
            return dt

        return dt.astimezone(dtz.tzutc()).replace(tzinfo=None)

    @staticmethod
    def getuser(mantis_user):
        name = None

        for i in ('real_name', 'name'):
            try:
                name = getattr(mantis_user, 'name')
                break
            except AttributeError:
                pass

        if not name:
            name = 'user{0}'.format(mantis_user.id)

        name = coerce_unicode(name)
        email = coerce_unicode(getattr(mantis_user, 'email', ''))

        logger.debug("Getting user (name=[%s], email=[%s])",
                     repr(name), repr(email))

        return get_participant(name, email)

    @transaction.atomic
    def _run(self):
        for project in self.projects:
            def get_issues():
                page = 1

                while True:
                    logger.info("Fetching issues for project [%s], page %s",
                                project.name, page)

                    try:
                        issues = project.get_issues(page, 100)

                    except WebFault:
                        logger.warn("Could not import things for project [%s],"
                                    "id=%s",
                                    project.name, project.id,
                                    exc_info=True)
                        break

                    # Short read. We're done
                    if not issues:
                        break

                    for issue in issues:
                        yield issue

                    page += 1

            for issue in get_issues():
                severity = self.translate_severity(issue.severity.name)
                bug, created = self.object.bugs.get_or_create(
                    bug_id=str(issue.id),
                    defaults=dict(
                        severity=self.translate_severity(issue.severity.name)
                    ))

                logger.info("%s bug [%s]",
                            "Created" if created else "Found", bug)

                if not created:
                    if bug.severity != severity:
                        bug.severity = severity
                        self.record_timestamp(timestamp)
                        bug.save()
                        self.record_timestamp(bug.timestamp)

                else:
                    logger.info("Saving initial comment for [%s]", bug)
                    bug.comments.create(
                        comment_id='VIRTUAL-1',
                        author=self.getuser(issue.reporter),
                        timestamp=self.sanitize_datetime(issue.date_submitted))
                    self.record_timestamp(timestamp)

                for note in getattr(issue, 'notes', []):
                    author = self.getuser(note.reporter)
                    timestamp = self.sanitize_datetime(note.date_submitted)

                    comment, created = bug.comments.get_or_create(
                        comment_id=note.id,
                        defaults={
                            'author': author,
                            'timestamp': timestamp
                        })

                    logger.info("%s comment [%s] on [%s]",
                                "Created" if created else "Found",
                                comment, bug)

                    if not created and (comment.author != author or
                                        comment.date_submitted != timestamp):
                        comment.author = author
                        comment.timestamp = timestamp
                        comment.save()
                        self.record_timestamp(timestamp)

BugTrackerImporter.register_importer('mantis', MantisImporter)
