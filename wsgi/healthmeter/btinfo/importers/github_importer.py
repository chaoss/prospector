# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import logging
import os
import re

from django.db import transaction

from grimoirelab.toolkit.datetime import str_to_datetime
from perceval.backends.core.github import GitHub

from .common import BugTrackerImporter
from healthmeter.hmeter_frontend.utils import get_participant

logger = logging.getLogger(__name__)


class GithubImporter(BugTrackerImporter):
    """
    Specialized importer class for importing bug information from github
    """
    users = {}

    def __init__(self, bt_info):
        super().__init__(bt_info)
        owner = bt_info.bug_tracker.baseurl.replace('http://github.com/', '')
        self.backend = GitHub(owner=owner,
                              repository=self.object.product,
                              api_token=bt_info.bug_tracker.api_token,
                              sleep_for_rate=True)

    def get_user(self, userdata):
        username = userdata['login']
        try:
            return self.users[username]
        except KeyError:
            pass

        # Sometimes github sends over these keys with null values
        retval = get_participant(userdata.get('name') or '',
                                 userdata.get('email') or '')
        self.users[username] = retval
        return retval

    @transaction.atomic
    def _run(self):
        issues_iter = self.backend.fetch()

        # Import all issues
        for issue_d in issues_iter:
            issue = issue_d['data']

            closed_at = issue['closed_at']
            if closed_at:
                closed_at = str_to_datetime(issue['closed_at'])

            bug, created = self.object.bugs.get_or_create(
                bug_id=str(issue['number']),
                defaults={'close_date': closed_at,
                          'severity': None})

            logger.info("%s bug [%s]",
                        "Imported" if created else "Found",
                        bug)

            if created:
                bug_create_time = str_to_datetime(issue['created_at'])
                comment = bug.comments.create(comment_id='VIRTUAL-1',
                                              author=self.get_user(
                                                  issue['user_data']),
                                              timestamp=bug_create_time)
                self.record_timestamp(bug_create_time)
                logger.info("Imported bug body as [%s]", comment)

        # TODO: not supported yet
        comments = []

        # Import comments
        for comment in comments:
            issue_number = os.path.basename(comment['issue_url'])
            bug = self.object.bugs.get(bug_id=issue_number)
            extrafields = {
                'author': self.get_user(comment['user']['login']),
                'timestamp': str_to_datetime(comment['created_at'])
            }
            comment, created = bug.comments.get_or_create(
                comment_id=comment['id'],
                defaults=extrafields)

            logger.info("%s comment [%s]",
                        "Imported" if created else "Found",
                        comment)

            if not created:
                for key, value in extrafields.items():
                    oldvalue = getattr(comment, key)
                    if oldvalue != value:
                        logger.warning("Updating field [%s] for comment [%s] "
                                       "(%s -> %s)", key, comment,
                                       oldvalue, value)
                        setattr(comment, key, value)
                        self.record_timestamp(comment.timestamp)

            else:
                self.record_timestamp(comment.timestamp)

BugTrackerImporter.register_importer('github', GithubImporter)
