# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""Common functions for vcs importers"""

import os
import re
import sys

import magic

from django.db import DatabaseError, transaction
from healthmeter.importerutils.importers import ImporterBase
from healthmeter.hmeter_frontend.utils import get_participant, coerce_unicode
from healthmeter.vcsinfo.models import Repository


_magic = magic.Magic(mime_encoding=True)


def _is_text(buf):
    return _magic.from_buffer(buf) != 'binary'


class VcsImporter(ImporterBase):
    model = Repository

    """Generic VCS Importer class"""
    @classmethod
    def resolve_importer_type(cls, dj_repo):
        return dj_repo.type.name

    def _get_checkout_path(self):
        """Returns a path to the vcs checkout"""
        path = os.path.join(os.getenv('OPENSHIFT_DATA_DIR',
                                      os.getenv('TMPDIR', '/tmp')),
                            'vcs-checkouts', str(self.object.pk))
        return path

    userid_regexes = [
        re.compile(regex)
        for regex in (r'(?P<name>[^<]+) +<(?P<email>[^>]+)>',
                      r'<(?P<email>[^>]+)>',
                      r'(?P<email>.*@.*)',
                      r'(?P<name>.*)')
    ]

    @classmethod
    def parseaddr(cls, userid):
        match = None
        for regex in cls.userid_regexes:
            match = regex.match(userid)
            if match:
                break

        groups = match.groupdict()
        return (groups.get('name', ''), groups.get('email', ''))

    def count_lines_from_buf(self, buf):
        if not _is_text(buf):
            return 0

        return buf.count('\n')

    def get_committer(self, name=None, email=None, userid=None):
        if name is not None:
            name = coerce_unicode(name)

        if email is not None:
            email = coerce_unicode(email)

        if userid is None:
            if name is None or email is None:
                raise TypeError("Either userid must be provided, "
                                "or both name and email must be provided.")

            userid = u"{0} <{1}>".format(name, email)

        else:
            userid = coerce_unicode(userid)
            name = name or ''
            email = email or ''

            if not name and not email:
                name, email = self.parseaddr(userid)
                if not name and '@' not in email:
                    name = email
                    email = ''

        # the following segment is lifted from .get_or_create(), with
        # lazy-constructed Participant.
        try:
            return self.object.committers.get(userid=userid)

        except self.object.committers.model.DoesNotExist:
            # race prone so try again if we fail to create this
            # basically a manual get_or_create with deferred
            try:
                with transaction.atomic():
                    participant = get_participant(name, email)
                    return self.object \
                               .committers \
                               .create(participant=participant,
                                       userid=userid)

            except DatabaseError:
                _, ei, tb = sys.exc_info()

                try:
                    return self.object.committers.get(userid=userid)
                except self.object.committers.model.DoesNotExist:
                    raise ei.with_traceback(tb)
