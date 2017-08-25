# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""This module contains the git importer for the healthmeter project"""

import logging
import os
from collections import deque

import dulwich
import dulwich.client
import dulwich.repo
import datetime
from django.db import transaction

import itertools
import re
import shutil
import stat

from healthmeter.hmeter_frontend.models import *
from healthmeter.vcsinfo.models import Branch
from .common import VcsImporter
from .dvcsimporter import DVcsImporter

logger = logging.getLogger(__name__)  # pylint: disable-msg=C0103


class GitImporter(DVcsImporter):
    def __init__(self, dj_repo):
        super(GitImporter, self).__init__(dj_repo)
        self._init_repository()
        self.cached_line_count = {}

    def _init_repository(self):
        logger.info("Initializing importer for repository [%s]",
                    self.object.url)
        self.repo_path = self._get_checkout_path()

        try:
            self.repo = dulwich.repo.Repo(self.repo_path)
            logger.info('Found repository at [%s]. Updating..', self.repo_path)

        except dulwich.repo.NotGitRepository:
            if os.path.exists(self.repo_path):
                logger.warn("[%s] is not a git repository! Purging..",
                            self.repo_path)

                if os.path.isdir(self.repo_path):
                    shutil.rmtree(self.repo_path)

                else:
                    os.remove(self.repo_path)

            logger.info('No repository at [%s]. Cloning..', self.repo_path)
            os.mkdir(self.repo_path)
            self.repo = dulwich.repo.Repo.init_bare(self.repo_path)

        client, path = dulwich.client.get_transport_and_path(self.object.url)
        self.refs = client.fetch(path, self.repo) or {}

        # Look for the HEAD sha (the git protocol does not show symbolic refs)
        head_sha = None
        for i in ('HEAD', 'refs/heads/master'):
            try:
                head_sha = self.refs['HEAD']
                break
            except KeyError:
                pass

        head_found = False
        # Copy fetched refs into the repository
        for ref, sha in self.refs.iteritems():
            if ref.endswith('^{}'):
                continue

            elif (not head_found and
                  ref.startswith('refs/heads/') and
                  (sha == head_sha or head_sha is None)):
                self.repo.refs.set_symbolic_ref('HEAD', ref)
                head_found = True

            self.repo[ref] = sha

    def get_branches(self):
        return self.repo.refs.subkeys('refs/heads/')

    def get_active_branch(self):
        head_ref = self.repo.refs.read_ref('HEAD')
        assert head_ref.startswith('ref: refs/heads/')

        return head_ref[len('ref: refs/heads/'):]

    def _get_tag_date(self, tag):
        tagobj = self.repo.get_object(self.repo.refs['refs/tags/' + tag])

        try:
            timestamp = tagobj.tag_time
        except AttributeError:
            try:
                # probably a commit
                timestamp = tagobj.commit_time
            except AttributeError:
                # whoops, it was a tag, but without a timestamp.
                timestamp = self.repo[tagobj.object[1]].commit_time

        return datetime.datetime.utcfromtimestamp(timestamp)

    def get_tags(self):
        tags = self.repo.refs.subkeys('refs/tags/')

        def tag_generator():
            for tag in tags:
                try:
                    date = self._get_tag_date(tag)
                    yield tag, date
                except:
                    logger.warn("Could not get date of tag [%s]", tag)

        return list(tag_generator())

    def get_commit_for_branch(self, branch):
        return self.repo.refs['refs/heads/' + branch]

    def get_parents_for_commit(self, commit):
        return self.repo[commit].parents

    userid_ext_hggit_regex = re.compile(r' ?ext:\(.*\) ?')

    def get_commit_authorship(self, commit):
        commit = self.repo[commit]
        # Sanitize ext:(....) blocks from GIT_AUTHOR_NAME. hg-git adds these
        # for metadata.
        userid = self.userid_ext_hggit_regex.sub(' ', commit.author)

        author = self.get_committer(userid=userid)
        timestamp = datetime.datetime.utcfromtimestamp(commit.commit_time)

        return (author, timestamp)

    def count_lines(self, commit):
        commit = self.repo[commit]

        return self._count_tree_lines(commit.tree, '')

    def _count_tree_lines(self, tree_id, path):
        try:
            return self.cached_line_count[tree_id]
        except KeyError:
            pass

        tree = self.repo[tree_id]
        count = 0

        for item in tree.iteritems():
            item_path = os.path.join(path, item.path)
            if item.mode == 57344:
                continue        # This is actually a submodule
            if stat.S_ISDIR(item.mode):
                count += self._count_tree_lines(item.sha, item_path)
            else:
                count += self._count_blob_lines(item.sha, item_path)

        self.cached_line_count[tree_id] = count
        return count

    def _count_blob_lines(self, blob_id, path):
        try:
            return self.cached_line_count[blob_id]
        except KeyError:
            pass

        blob = self.repo[blob_id]

        logger.info("Counting lines in [%s]", path)
        count = self.count_lines_from_buf(blob.data)

        self.cached_line_count[blob_id] = count

        return count

    def close(self):
        """
        Delete the VCS checkout after use. We're running out of disk space
        """
        shutil.rmtree(self.repo_path)

VcsImporter.register_importer('git', GitImporter)
