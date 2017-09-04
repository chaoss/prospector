# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging

from django.db import transaction

from grimoirelab.toolkit.datetime import str_to_datetime
from perceval.backends.core.jira import Jira

from .common import BugTrackerImporter
from healthmeter.hmeter_frontend.utils import get_participant

logger = logging.getLogger(__name__)


class JIRAImporter(BugTrackerImporter):
    severity_level_map = {
        'Blocker': 4,
        'Critical': 4,
        'Major': 3,
        'Minor': 2,
        'Optional': 1,
        'Trivial': 1,
    }

    def __init__(self, bt_info):
        super().__init__(bt_info)

        self.backend = Jira(bt_info.bug_tracker.baseurl,
                            user=bt_info.bug_tracker.username,
                            password=bt_info.bug_tracker.password)

    def _import_comment(self, bug, comment_id, author, timestamp):
        """
        Import comment into `bug'.

        @arg bug btinfo.models.Bug object to import comment for
        @arg comment_id String representing comment ID
        @arg author Jira user
        @arg timestamp String timestamp in iso8601 form

        @returns True if comment was created, otherwise false
        """
        timestamp = str_to_datetime(timestamp)

        name = author['displayName']
        email = author.get('emailAddress', None)

        author = get_participant(name, email)

        _, created = bug.comments.get_or_create(
            comment_id=comment_id,
            defaults={
                'author': author,
                'timestamp': timestamp})

        if created:
            self.record_timestamp(timestamp)

        return created

    def iter_bugs(self):
        issues = self.backend.fetch()

        for issue in issues:
            yield issue

    def _run(self):
        for bug in self.iter_bugs():
            issue = bug['data']
            cl_date = issue['fields']['resolutiondate']

            if cl_date:
                close_date = str_to_datetime(cl_date)
            else:
                close_date = None

            try:
                with transaction.atomic():
                    bug, created = self.object.bugs.get_or_create(
                        bug_id=issue['key'],
                        defaults={'close_date': close_date})

                    logger.info("%s bug [%s]",
                                "Imported" if created else "Found",
                                issue['key'])

                    # Create first comment, since that seems to be merged into
                    # the issue
                    if created:
                        self._import_comment(bug, 'VIRTUAL-1',
                                             issue['fields']['reporter'],
                                             issue['fields']['created'])

                    # We didn't import a new bug, so set the .close_date
                    else:
                        bug.close_date = close_date
                        bug.save()

                    # TODO: comments not supported yet
                    comments = []

                    for comment in comments:
                        created_comment = self._import_comment(bug, comment.id,
                                                               comment.author,
                                                               comment.created)

                        logger.info("%s comment [%s]",
                                    "Imported" if created_comment else "Found",
                                    comment.id)
            except:
                logger.info("Couldn't import issue [%s], skipping", issue,
                            exc_info=True)

BugTrackerImporter.register_importer('jira', JIRAImporter)
