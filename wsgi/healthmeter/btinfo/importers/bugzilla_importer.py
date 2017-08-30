# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import bugzilla
import datetime
from dateutil.parser import parse as parsedate
import logging
import types
import unicodedata
import xmlrpclib
from xml.parsers.expat import ExpatError

from django.db import IntegrityError, transaction

from healthmeter.btinfo.models import Severity
from healthmeter.hmeter_frontend.utils import get_participant

from .common import BugTrackerImporter

logger = logging.getLogger(__name__)


class FilterParser(object):
    """
    Filtering object that strips control characters before actually parsing
    """
    def __init__(self, parser):
        self.parser = parser

    def __getattr__(self, attr):
        """Pass through to bound methods of self.parser"""
        return getattr(self.parser, attr)

    def feed(self, data):
        """
        Overridden feed(data) method which strips control characters before
        passing to the underlying parser.feed(data) method.

        See xmlrpclib.ExpatParser.feed
        """
        data = ''.join(c for c in data.decode('utf-8', 'replace')
                       if c == '\n'
                       or unicodedata.category(c) != 'Cc').encode('utf-8')
        self.parser.feed(data)


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

        xmlrpc_url = bt_info.bug_tracker.baseurl
        if 'xmlrpc.cgi' not in xmlrpc_url:
            xmlrpc_url += '/xmlrpc.cgi'
        self.bg = bugzilla.Bugzilla(url=xmlrpc_url, cookiefile=None)

        # Override getparser method of transport
        # TODO: upgrade to python-bugzilla 0.9.0 for self.bg._transport
        transport = self.bg._proxy._ServerProxy__transport
        transportcls = transport.__class__
        orig_getparser = transport.getparser

        def getparser(self):
            """
            Creates a parser. See xmlrpclib.Transport.getparser.
            """
            parser, unmarshaller = orig_getparser()
            parser = FilterParser(parser)
            return parser, unmarshaller

        transport.getparser = types.MethodType(getparser, transport,
                                               transportcls)

        # login if necessary
        username = bt_info.bug_tracker.username
        password = bt_info.bug_tracker.password
        if username and password:
            self.bg.login(username, password)

        # Don't query comments together with bugs
        try:
            self.bg.getbug_extra_fields.remove('comments')
        except:
            pass

        logger.info("Initialized bugzilla importer with url: [%s]", xmlrpc_url)

        self.user_cache = {}

    def get_user(self, user):
        try:
            return self.user_cache[user]
        except KeyError:
            logger.info("User [%s] not in cache, querying bugzilla", user)
            userobj = self.bg.getuser(user)
            self.user_cache[user] = userobj
            return userobj

    def iter_bugs(self):
        query_args = {}
        if self.object.product:
            query_args['product'] = self.object.product

        if self.object.component:
            query_args['component'] = self.object.component

        offset = 0
        limit = 200

        while True:
            query_args.update({'offset': offset,
                               'limit': limit})
            current_bugs = self.bg.query(query_args)

            if not current_bugs:
                break

            offset += limit

            bug_ids = [b.id for b in current_bugs]
            commentdict = self.bg._proxy.Bug.comments({'ids': bug_ids})['bugs']

            for bug in current_bugs:
                try:
                    bug.comments = commentdict[str(bug.id)]['comments']
                except KeyError:
                    bug.comments = []

            all_comments = (comment
                            for k, v in commentdict.iteritems()
                            for comment in v['comments'])

            # Prepopulate user cache
            missing_users = set(comment['author'] for comment in all_comments
                                if comment['author'] not in self.user_cache)
            if missing_users:
                missing_users = list(missing_users)
                logger.info("Prepopulating user cache with %s",
                            missing_users)
                self.user_cache.update(
                    dict((user.name, user)
                         for user in self.bg.getusers(missing_users)))

            # Actual generator code
            for bug in current_bugs:
                if not bug.comments:
                    logger.warning("No comments for bug [%s], skipping.",
                                    bug.id)
                yield bug

    def _run(self):
        q = self.object.bugs.all()

        for bug in self.iter_bugs():
            logger.info("Got bug [%s] from server", bug.id)

            dj_bug, created = q.get_or_create(
                tracker_info=self.object, bug_id=bug.id)

            logger.info("%s bug [%s]", "Imported" if created else "Found",
                        bug.id)

            # Because sometimes the attribute doesn't exist, and sometimes it's
            # None. Check __dict__ directly to avoid python-bugzilla's
            # autorefreshing if it doesn't exist.
            if 'cf_last_closed' in bug.__dict__ and bug.cf_last_closed:
                last_closed_date = bug.cf_last_closed

            # FIXME: For now we assume that the last change time is when the
            # bug was closed, but that is not always the case. We should look
            # into calling Bug::history to get this information.
            elif bug.resolution:
                last_closed_date = bug.last_change_time

            else:
                last_closed_date = None

            # HACK: Work around inconsistency in last_closed_date type.
            # Sometimes it's xmlrpclib.DateTime, sometimes it's a string.
            last_closed_date = (last_closed_date and
                                parsedate(str(last_closed_date)))

            # Work around bug in some versions of bugzilla which caused
            # last_closed to be set to 0 instead of Null.
            if last_closed_date == datetime.datetime.utcfromtimestamp(0):
                last_closed_date = None

            if last_closed_date and last_closed_date != dj_bug.close_date:
                self.record_timestamp(last_closed_date)

            dj_bug.close_date = last_closed_date

            dj_bug.severity = self.translate_severity(bug.severity)
            dj_bug.save()

            for comment in bug.comments:
                logger.debug("Comment is: %s", comment)
                commenter = self.get_user(comment['author'])
                author = get_participant(commenter.real_name,
                                         commenter.email)
                posting_date = parsedate(str(comment['time']))

                # If timezone is present, force into UTC and strip -- DB is
                # not tz-aware
                if posting_date.tzinfo is not None:
                    posting_date = posting_date \
                        .astimezone(iso8601.iso8601.UTC) \
                        .replace(tzinfo=None)

                dj_comment, created = dj_bug.comments.get_or_create(
                    comment_id=comment['id'],
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
                            comment['id'], bug.id)

            transaction.commit_unless_managed()

BugTrackerImporter.register_importer('bugzilla', BugzillaImporter)
