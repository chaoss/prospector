# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import hglib
import os
import shutil
from .dvcsimporter import DVcsImporter


class HgImporter(DVcsImporter):
    def __init__(self, dj_repo):
        super(HgImporter, self).__init__(dj_repo)
        self.repo_path = self._get_checkout_path()
        shutil.rmtree(self.repo_path)
        self.client = hglib.clone(source=self.object.url,
                                  dest=self.repo_path)

        # Workaround bug in hglib that causes hg cat to complain about missing
        # paths
        os.chdir(self.repo_path)
        self.client.open()

        self.cached_line_count = {}

    def get_branches(self):
        return [branch_info[0] for branch_info in self.client.branches()]

    def get_active_branch(self):
        return self.client.summary()['branch']

    def _get_commit_info(self, rev):
        return self.client.log('{0}:{0}'.format(rev))[0]

    def get_tags(self):
        return [(tag, self._get_commit_info(nodeid)[6])
                for tag, _, nodeid, _
                in self.client.tags()
                if tag != 'tip']

    def get_commit_for_branch(self, branch):
        return self.client.log('{0}:{0}'.format(branch))[0][1]

    def get_parents_for_commit(self, commit):
        commits = self.client.parents(commit) or []
        return [commit[1] for commit in commits]

    def get_commit_authorship(self, commit):
        commit = self._get_commit_info(commit)
        author = self.get_committer(userid=commit[4])
        timestamp = commit[6]

        return (author, timestamp)

    def count_lines(self, commit, nodeid=None, path=None):
        # Check if we need to recurse
        if nodeid is None:
            return sum(self.count_lines(commit, nodeid, path)
                       for nodeid, _, _, _, path in
                       self.client.manifest(commit))

        # Next check if it's cached
        try:
            return self.cached_line_count[nodeid]
        except KeyError:
            pass

        # Finally, count and store in cache
        count = self.count_lines_from_buf(self.client.cat([path], rev=commit))
        self.cached_line_count[nodeid] = count

        return count

HgImporter.register_importer('hg', HgImporter)
