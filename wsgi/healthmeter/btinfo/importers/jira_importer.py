# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import IntegrityError, transaction
import iso8601
from jira.client import JIRA
from jira.exceptions import JIRAError
import logging

from healthmeter.btinfo.models import Severity

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
        super(JIRAImporter, self).__init__(bt_info)

        options = {'server': bt_info.bug_tracker.baseurl,
                   'verify': False}

        username = bt_info.bug_tracker.username
        password = bt_info.bug_tracker.password

        basic_auth = (username, password) if username and password else None

        self.jira = JIRA(options=options, basic_auth=basic_auth)

    @staticmethod
    def _parse_timestamp(timestamp):
        timestamp = iso8601.parse_date(timestamp)
        if timestamp.tzinfo is not None:
            timestamp = timestamp \
                .astimezone(iso8601.iso8601.UTC) \
                .replace(tzinfo=None)

        return timestamp

    def _import_comment(self, bug, comment_id, author, timestamp):
        """
        Import comment into `bug'.

        @arg bug btinfo.models.Bug object to import comment for
        @arg comment_id String representing comment ID
        @arg author Jira user
        @arg timestamp String timestamp in iso8601 form

        @returns True if comment was created, otherwise false
        """
        timestamp = JIRAImporter._parse_timestamp(timestamp)

        author = get_participant(author.displayName, author.emailAddress)

        _, created = bug.comments.get_or_create(
            comment_id=comment_id,
            defaults={
                'author': author,
                'timestamp': timestamp})

        if created:
            self.record_timestamp(timestamp)

        return created

    def iter_bugs(self):
        query = ('project="{0}"'.format(self.object.product)
                 if self.object.product else '')
        if self.object.component:
            query += 'and component="{0}"'.format(self.object.component)

        query += ' order by created asc'

        offset = 0
        limit = None
        while limit is None or offset < limit:
            tries = 5
            issues = None
            while issues is None:
                try:
                    issues = self.jira.search_issues(query, startAt=offset,
                                                     maxResults=500)
                except JIRAError as e:
                    tries -= 1

                    logger.warn("Caught JIRAError while querying at offset "
                                "[%s]. Tries remaining=%s",
                                offset, tries,
                                exc_info=True)

                    if not tries:
                        raise

            limit = issues.total

            for issue in issues:
                yield issue

            offset += len(issues)

    def _run(self):
        for issue in self.iter_bugs():
            try:
                close_date = self._parse_timestamp(issue.fields.resolutiondate)
            except iso8601.ParseError:
                close_date = None

            try:
                with transaction.commit_on_success():
                    bug, created = self.object.bugs.get_or_create(
                        bug_id=issue.key,
                        defaults={'close_date': close_date})

                    logger.info("%s bug [%s]",
                                "Imported" if created else "Found",
                                issue.key)

                    # Create first comment, since that seems to be merged into
                    # the issue
                    if created:
                        self._import_comment(bug, 'VIRTUAL-1',
                                             issue.fields.reporter,
                                             issue.fields.created)

                    # We didn't import a new bug, so set the .close_date
                    else:
                        bug.close_date = close_date
                        bug.save()

                    comments = self.jira.comments(issue)

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
