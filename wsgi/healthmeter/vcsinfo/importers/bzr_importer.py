# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""This module contains the bzr importer for the healthmeter project"""

import bzrlib
import bzrlib.plugin
import bzrlib.branch
import datetime
from django.db import transaction
from email.utils import parseaddr
import logging

from .common import VcsImporter
from .dvcsimporter import DVcsImporter

bzrlib.initialize()
bzrlib.plugin.load_plugins()
logger = logging.getLogger(__name__)


class BzrImporter(DVcsImporter):
    def __init__(self, dj_repo):
        super(BzrImporter, self).__init__(dj_repo)
        self.branch = bzrlib.branch.Branch.open(dj_repo.url)

    def get_branches(self):
        return [self.get_active_branch()]

    def get_active_branch(self):
        return self.branch.nick

    def get_tags(self):
        tag_dict = self.branch.tags.get_tag_dict()

        def _gen():
            for tag, revstr in tag_dict.items():
                try:
                    revision = self.branch \
                                   .repository \
                                   .get_revision(revstr)
                    date = datetime.datetime \
                                   .utcfromtimestamp(revision.timestamp) \
                                   .date()
                except:
                    logger.warn("Couldn't import tag [%s] with revstr [%s]",
                                tag, revstr, exc_info=True)

                yield (tag, date)

        return list(_gen())

    def get_commit_for_branch(self, branch):
        assert branch == self.branch.nick

        return self.branch.last_revision()

    def get_parents_for_commit(self, commit):
        commit = self.branch.repository.get_revision(commit)
        return commit.parent_ids

    def get_commit_authorship(self, commit):
        commit = self.branch.repository.get_revision(commit)
        name, email = parseaddr(commit.committer)
        committer = self.get_committer(name=name, email=email)

        return (committer,
                datetime.datetime.utcfromtimestamp(commit.timestamp).date())

    def count_lines(self, commit):
        return 0

VcsImporter.register_importer('bzr', BzrImporter)
