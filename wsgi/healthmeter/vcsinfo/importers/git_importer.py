# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""This module contains the git importer for the healthmeter project"""

import logging
import re

import grimoirelab.toolkit.datetime
import perceval.backends.core.git as git

from healthmeter.hmeter_frontend.models import *

from .common import VcsImporter
from .dvcsimporter import DVcsImporter

logger = logging.getLogger(__name__)  # pylint: disable-msg=C0103


class GitImporter(DVcsImporter):
    def __init__(self, dj_repo):
        super().__init__(dj_repo)
        self.backend = None
        self._init_repository()
        self.cached_line_count = {}

    def _init_repository(self):
        logger.info("Initializing importer for repository [%s]",
                    self.object.url)
        self.repo_path = self._get_checkout_path()

        self.backend = git.Git(self.object.url, self.repo_path)

    userid_ext_hggit_regex = re.compile(r' ?ext:\(.*\) ?')

    def get_commit_authorship(self, commit):
        data = commit['data']

        # Sanitize ext:(....) blocks from GIT_AUTHOR_NAME. hg-git adds these
        # for metadata.
        userid = self.userid_ext_hggit_regex.sub(' ', data['Author'])

        author = self.get_committer(userid=userid)
        timestamp = grimoirelab.toolkit.datetime.str_to_datetime(data['CommitDate'])

        return (author, timestamp)

    def count_lines(self, commit):
        # TODO: not implemented yet
        return 0

VcsImporter.register_importer('git', GitImporter)
