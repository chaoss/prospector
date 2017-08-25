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
    def get_branches(self):
        """Return list of branches"""
        pass

    @abc.abstractmethod
    def get_active_branch(self):
        """Return name of active branch"""
        pass

    @abc.abstractmethod
    def get_tags(self):
        """Return list of (tag, datetime.date) tuples"""
        pass

    @abc.abstractmethod
    def get_commit_for_branch(self, branch):
        """Return commit ID at head of branch"""
        pass

    @abc.abstractmethod
    def get_parents_for_commit(self, commit):
        """
        Get parents of a commit.

        @arg commit Commit ID to lookup parents for
        @returns Set of commit IDS
        """
        pass

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

    @transaction.commit_on_success
    def _run(self):
        branches = self.get_branches()
        active_branch = self.get_active_branch()

        for branch in branches:
            logger.info("Importing commits for branch [%s]", branch)
            branch_commit = self.get_commit_for_branch(branch)
            commit_stack = [branch_commit]

            while commit_stack:
                current_commit = commit_stack.pop()
                current_parents = set(
                    self.get_parents_for_commit(current_commit))

                dj_parents = self.object \
                                 .commits.filter(commit_id__in=current_parents)
                dj_parents_hashes = set(c.commit_id for c in dj_parents)

                if len(dj_parents_hashes) != len(current_parents):
                    logger.info("Commit [%s] parents not complete. "
                                "Adding to stack..",
                                current_commit)

                    commit_stack.append(current_commit)
                    commit_stack.extend(current_parents - dj_parents_hashes)
                    continue

                line_count = self.count_lines(current_commit)
                author, timestamp = self.get_commit_authorship(current_commit)

                logger.info("Importing commit [%s]...", current_commit)
                dj_commit, created = self.object.commits.get_or_create(
                    commit_id=current_commit,
                    defaults={
                        'author': author,
                        'timestamp': timestamp,
                        'line_count': line_count
                    })

                if created:
                    self.record_timestamp(timestamp)

                else:
                    logger.info("[%s] already in database. Skipping parents.",
                                current_commit)
                    continue

                for parent in dj_parents:
                    logger.info("Adding [%s] -> [%s] link",
                                current_commit, parent)
                    parent.add_child(dj_commit, disable_circular_check=True)

                transaction.commit()

            assert current_commit == branch_commit

            dj_branch, created = self.object.branches.get_or_create(
                name=branch,
                defaults={'latest_commit': dj_commit}
            )

            if not created:
                dj_branch.latest_commit = dj_commit
                dj_branch.save()

        # Cleanup old branches
        old_branches = self.object.branches.exclude(name__in=branches)
        logger.info("Cleaning up old branches: %s", list(old_branches))
        old_branches.delete()

        # Update main branch
        self.object.branches.exclude(name=active_branch) \
                            .update(is_main=False)
        active_count = self.object.branches.filter(name=active_branch) \
                                           .update(is_main=True)
        assert active_count <= 1

        for tag, date in self.get_tags():
            release, created = self.object.project.releases \
                .get_or_create(version=tag, defaults={'date': date})

            logger.info("%s release [%s]", "Imported" if created else "Found",
                        tag)

            if created:
                self.record_timestamp(date)
