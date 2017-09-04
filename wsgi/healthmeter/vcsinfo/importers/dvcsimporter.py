# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""Abstracted algorithm for importing DVCS repositories"""

import abc
from django.db import transaction
import logging

from .common import VcsImporter

logger = logging.getLogger(__name__)


class DVcsImporter(VcsImporter):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_commit_authorship(self, commit):
        """
        Get the authorship information for this commit

        @arg commit Commit ID to lookup authorship information for
        @returns (author, timestamp) tuple
        """
        pass

    @abc.abstractmethod
    def count_lines(self, commit):
        """
        Get the SLOC for the commit.

        @arg commit Commit ID to count lines for
        @returns integer containing lines of code for the commit

        """
        pass

    @transaction.atomic
    def _run(self):
        logger.info("Importing commits for repository [%s]", self.object.url)
        commit_stack = self.backend.fetch(latest_items=True)

        for current_commit in commit_stack:
            line_count = self.count_lines(current_commit)
            author, timestamp = self.get_commit_authorship(current_commit)

            logger.info("Importing commit [%s]...", current_commit)
            _, created = self.object.commits.get_or_create(
                commit_id=current_commit['data']['commit'],
                defaults={
                    'author': author,
                    'timestamp': timestamp,
                    'line_count': line_count
                })

            if created:
                self.record_timestamp(timestamp)
            else:
                logger.info("[%s] already in database. Skipping.",
                            current_commit)
                continue
