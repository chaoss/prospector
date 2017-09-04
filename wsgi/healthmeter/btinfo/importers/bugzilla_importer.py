# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
import logging

from django.db import transaction

from grimoirelab.toolkit.datetime import str_to_datetime
from perceval.backends.core.bugzilla import Bugzilla

from healthmeter.hmeter_frontend.utils import get_participant

from .common import BugTrackerImporter


logger = logging.getLogger(__name__)


class BugzillaImporter(BugTrackerImporter):
    """
    Specialized importer class for importing bug information from Bugzilla
    """
    severity_level_map = {
        'wishlist': 1,
        'enhancement': 1,
        'p1': 1,
        'p2': 1,
        'trivial': 1,
        'low': 1,
        'minor': 1,
        'p3': 2,
        'medium': 2,
        'normal': 2,
        'nor': 2,
        'p4': 3,
        'high': 3,
        'major': 3,
        'grave': 3,
        'crash': 3,
        'p5': 4,
        'urgent': 4,
        'immediate': 4,
        'critical': 4,
        'blocker': 4
    }

    def __init__(self, bt_info):
        super().__init__(bt_info)
        self.backend = Bugzilla(bt_info.bug_tracker.baseurl,
                                user=bt_info.bug_tracker.username,
                                password=bt_info.bug_tracker.password)

        logger.info("Initialized bugzilla importer with url: [%s]",
                    bt_info.bug_tracker.baseurl)

    def iter_bugs(self):
        bugs = self.backend.fetch()
        for bug in bugs:
            yield bug

    def _run(self):
        q = self.object.bugs.all()

        for issue in self.iter_bugs():
            bug = issue['data']
            bug_id = bug['bug_id'][0]['__text__']
            logger.info("Got bug [%s] from server", bug_id)

            dj_bug, created = q.get_or_create(
                tracker_info=self.object, bug_id=bug_id)

            logger.info("%s bug [%s]", "Imported" if created else "Found",
                        bug_id)

            # Because sometimes the attribute doesn't exist, and sometimes it's
            # None. Check directly to avoid python-bugzilla's
            # autorefreshing if it doesn't exist.
            if 'cf_last_closed' in bug and bug['cf_last_closed'][0]['__text__']:
                last_closed_date = bug['cf_last_closed'][0]['__text__']


            # FIXME: For now we assume that the last change time is when the
            # bug was closed, but that is not always the case. We should look
            # into calling Bug::history to get this information.
            elif bug['resolution']:
                last_closed_date = bug['delta_ts'][0]['__text__']
            else:
                last_closed_date = None

            if last_closed_date:
                last_closed_date = str_to_datetime(last_closed_date)

            if last_closed_date and last_closed_date != dj_bug.close_date:
                self.record_timestamp(last_closed_date)

            dj_bug.close_date = last_closed_date

            dj_bug.severity = self.translate_severity(bug['bug_severity'][0]['__text__'])
            dj_bug.save()
            if 'long_desc' not in bug:
                bug['long_desc'] = []

            for comment in bug['long_desc']:
                comment_id = comment['commentid'][0]['__text__']
                logger.debug("Comment is: %s", comment_id)

                author = comment['who'][0]
                real_name = author['name']
                email = author['__text__']
                if email.find('@') < 0:
                    email = None
                author = get_participant(real_name, email)
                posting_date = str_to_datetime(comment['bug_when'][0]['__text__'])

                dj_comment, created = dj_bug.comments.get_or_create(
                    comment_id=comment_id,
                    defaults=dict(timestamp=posting_date,
                                  author=author))

                dirty = False
                if dj_comment.timestamp != posting_date:
                    dirty = True
                    dj_comment.timestamp = posting_date
                    logger.warning("Fixing timestamp of [%s]",
                                   dj_comment)
                if dj_comment.author != author:
                    dirty = True
                    logger.warning("Fixing author of [%s], from [%s] to [%s]",
                                   dj_comment, dj_comment.author, author)
                    dj_comment.author = author

                if dirty:
                    dj_comment.save()

                if dirty or created:
                    self.record_timestamp(posting_date)

                logger.info("%s comment [%s, %s]",
                            "Imported" if created else "Found",
                            comment_id, bug_id)

            transaction.atomic()

BugTrackerImporter.register_importer('bugzilla', BugzillaImporter)
