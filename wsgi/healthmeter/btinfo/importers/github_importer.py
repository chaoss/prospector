# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import dateutil.parser as dparser
import dateutil.tz as dtz
import datetime
import logging
import os
import re
import requests
import rfc822

from django.db import transaction

from .common import BugTrackerImporter
from healthmeter.hmeter_frontend.utils import get_participant

logger = logging.getLogger(__name__)


class GithubError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self, message, status_code)


class GithubImporter(BugTrackerImporter):
    """
    Specialized importer class for importing bug information from github
    """
    basepath = 'https://api.github.com/'
    users = {}
    link_regex = re.compile(r'<(?P<url>[^>]+)>; rel="(?P<type>[^"]+)"')

    def query(self, url, **kwargs):
        try:
            session = self.session
        except AttributeError:
            session = self.session = requests.session()

        kwargs.setdefault('params', {})['per_page'] = '100'  # max items

        if ((self.object.bug_tracker.username and
             self.object.bug_tracker.password)):
            kwargs.setdefault('auth',
                              (self.object.bug_tracker.username,
                               self.object.bug_tracker.password))

        result = None

        while url is not None:
            logger.info("Querying [%s]", url)

            response = session.get(url, **kwargs)
            if response.status_code != 200:
                raise GithubError("Invalid response from server",
                                  response.status_code)

            logger.info("Received response. Ratelimit remaining: [%s/%s]. "
                        "Reset at [%s]",
                        response.headers['x-ratelimit-remaining'],
                        response.headers['x-ratelimit-limit'],
                        datetime.datetime.utcfromtimestamp(
                            int(response.headers['x-ratelimit-reset'])))
            json = response.json()
            assert type(json) == type(result) or result is None

            if isinstance(result, dict):
                result.update(json)
            elif isinstance(result, list):
                result.extend(json)
            else:
                result = json

            links = dict((groups['type'], groups['url'])
                         for groups in (match.groupdict()
                                        for match in
                                        self.link_regex.finditer(
                                            response.headers.get('link', ''))))

            url = links.get('next', None)

        return result

    def get_user(self, username):
        try:
            return self.users[username]
        except KeyError:
            pass

        userinfo = self.query(os.path.join(self.basepath, 'users', username))

        # Sometimes github sends over these keys with null values
        retval = get_participant(userinfo.get('name') or '',
                                 userinfo.get('email') or '')
        self.users[username] = retval
        return retval

    def parsedate(self, datestr):
        if datestr is None:
            return None

        return dparser.parse(datestr).astimezone(dtz.tzutc()) \
                                     .replace(tzinfo=None)

    @transaction.commit_on_success
    def _run(self):
        repo_url = os.path.join(self.basepath, 'repos', self.object.product)

        # Query comments first to ensure we don't see parentless comments
        comments = self.query(os.path.join(repo_url, 'issues/comments'),
                              params={'sort': 'created',
                                      'direction': 'asc'})
        issues_url = os.path.join(repo_url, 'issues')
        issues_params = {'state': 'open',
                         'sort': 'created',
                         'direction': 'asc'}
        issues = self.query(issues_url, params=issues_params)
        issues_params['state'] = 'closed'
        issues += self.query(issues_url, params=issues_params)

        # Import all issues
        for issue in issues:
            bug, created = self.object.bugs.get_or_create(
                bug_id=str(issue['number']),
                defaults={'close_date': self.parsedate(issue['closed_at']),
                          'severity': None})

            logger.info("%s bug [%s]",
                        "Imported" if created else "Found",
                        bug)

            if created:
                bug_create_time = self.parsedate(issue['created_at'])
                comment = bug.comments.create(comment_id='VIRTUAL-1',
                                              author=self.get_user(
                                                  issue['user']['login']),
                                              timestamp=bug_create_time)
                self.record_timestamp(bug_create_time)
                logger.info("Imported bug body as [%s]", comment)

        comments_url = os.path.join(self.basepath, 'repos',
                                    self.object.product,
                                    'issues/comments')

        # Import comments
        for comment in comments:
            issue_number = os.path.basename(comment['issue_url'])
            bug = self.object.bugs.get(bug_id=issue_number)
            extrafields = {
                'author': self.get_user(comment['user']['login']),
                'timestamp': self.parsedate(comment['created_at'])
            }
            comment, created = bug.comments.get_or_create(
                comment_id=comment['id'],
                defaults=extrafields)

            logger.info("%s comment [%s]",
                        "Imported" if created else "Found",
                        comment)

            if not created:
                for key, value in extrafields.items():
                    oldvalue = getattr(comment, key)
                    if oldvalue != value:
                        logger.warning("Updating field [%s] for comment [%s] "
                                       "(%s -> %s)", key, comment,
                                       oldvalue, value)
                        setattr(comment, key, value)
                        self.record_timestamp(comment.timestamp)

            else:
                self.record_timestamp(comment.timestamp)

BugTrackerImporter.register_importer('github', GithubImporter)
