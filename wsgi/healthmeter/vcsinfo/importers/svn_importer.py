# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""This module contains the svn importer for the healthmeter project"""

import datetime
from django.db import transaction
import logging
import os
import pysvn

from .common import VcsImporter

logger = logging.getLogger(__name__)


class SvnImporter(VcsImporter):
    def __init__(self, dj_repo):
        super(SvnImporter, self).__init__(dj_repo)
        self.client = pysvn.Client('/dev/null')

    @transaction.commit_on_success
    def _run(self):
        try:
            prev_commit = self.object.branches \
                .select_related('latest_commit') \
                .get(is_main=True).latest_commit

        except self.object.branches.model.DoesNotExist:
            prev_commit = None

        logger.info("Getting log for [%s] from revision [%s]",
                    self.object.url,
                    prev_commit.commit_id if prev_commit else '')

        kwargs = {}
        if prev_commit is not None:
            kwargs['revision_end'] = pysvn.Revision(
                pysvn.opt_revision_kind.number,
                prev_commit.commit_id)

        logs = self.client.log(self.object.url, **kwargs)
        logs_iter = reversed(logs)

        if prev_commit is not None:
            logs_iter.next()        # skip the first item (== prev_commit)

        for logentry in logs_iter:
            author_login = logentry.get('author', None)

            # SVN allows authorless commits -- just skip over those, I don't
            # think it makes sense to import them.
            if not author_login:
                continue

            commit_id = str(logentry['revision'].number)
            timestamp = datetime.datetime.utcfromtimestamp(logentry['date'])
            author = self.get_committer(userid=author_login)

            logger.info("Importing commit [%s], author=%s, timestamp=%s",
                        commit_id, author, timestamp)

            commit = self.object.commits.create(commit_id=commit_id,
                                                author=author,
                                                timestamp=timestamp)

            self.record_timestamp(timestamp)

            if prev_commit is not None:
                logger.info("Adding parent link from [%s] to [%s]",
                            commit, prev_commit)
                commit.add_parent(prev_commit, disable_circular_check=True)

            prev_commit = commit

        trunk_branch, created = self.object.branches \
            .get_or_create(name='trunk',
                           defaults={
                               'is_main': True,
                               'latest_commit': prev_commit
                           })
        if not created:
            trunk_branch.latest_commit = prev_commit
            trunk_branch.save()

VcsImporter.register_importer('svn', SvnImporter)
