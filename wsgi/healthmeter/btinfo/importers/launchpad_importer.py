# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import transaction
from healthmeter.hmeter_frontend.utils import get_participant
from launchpadlib.credentials import Credentials
from launchpadlib.launchpad import Launchpad
import logging
import os
from .common import BugTrackerImporter

logger = logging.getLogger(__name__)


class LaunchpadImporter(BugTrackerImporter):
    severity_level_map = {'Wishlist': 1,
                          'Low': 1,
                          'Medium': 2,
                          'High': 3,
                          'Critical': 4}

    closed_statuses = set([
        'Opinion',
        'Invalid',
        'Expired',
        'Fix Released'
    ])

    def __init__(self, *args, **kwargs):
        super(LaunchpadImporter, self).__init__(*args, **kwargs)
        self.usercache = {}

    def getuser(self, user):
        try:
            return self.usercache[user.name]
        except KeyError:
            try:
                email = user.preferred_email_address.email
            except (ValueError, AttributeError):  # email is hidden
                email = ''

            name = user.display_name
            djuser = self.usercache[user.name] = get_participant(name, email)
            return djuser

    def _run(self):
        credentials = Credentials.from_string(
            self.object.bug_tracker.password.encode("ascii"))
        lp = Launchpad(credentials, None, None, service_root="production")

        project = lp.projects[self.object.product]

        logger.info("Importing bugs from [%s]", project)
        for bug_task in project.searchTasks():
            close_date = (bug_task.date_closed
                          if bug_task.status in self.closed_statuses else
                          None)
            severity = self.translate_severity(bug_task.importance)
            bug = bug_task.bug

            logger.info("Processing bug [%s]", bug)

            with transaction.atomic():
                dj_bug, created = self.object.bugs.get_or_create(
                    bug_id=bug.id,
                    defaults={
                        'close_date': close_date,
                        'severity': severity
                    })

                logger.info("%s bug [%s]",
                            "Created" if created else "Found",
                            dj_bug)

                if created:
                    if close_date is not None:
                        self.record_timestamp(close_date)

                    dj_bug.comments.create(
                        comment_id='VIRTUAL-1',
                        author=self.getuser(bug.owner),
                        timestamp=bug.date_created)

                    self.record_timestamp(bug.date_created)

            for message in bug.messages:
                comment_id = os.path.basename(message.self_link)
                dj_comment, created = dj_bug.comments.get_or_create(
                    comment_id=comment_id,
                    defaults={
                        'timestamp': message.date_created,
                        'author': self.getuser(message.owner)
                    })

                logger.info("%s comment [%s]",
                            "Created" if created else "Found",
                            dj_comment)

                if created:
                    self.record_timestamp(message.date_created)

BugTrackerImporter.register_importer('launchpad', LaunchpadImporter)
