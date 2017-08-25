# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.test import TestCase, TransactionTestCase
from django.core.management import call_command
from iso8601 import iso8601
import itertools
from mocker import Mocker, expect, MATCH, ARGS, KWARGS, ANY
import requests
import simplejson

from .importers.jamiq import JamiqImporter, JamiqError
from .importers.jamiqtopic import JamiqTopicImporter
from .models import Project
from healthmeter.jamiqinfo.models import Credential, Topic


class MockJamiqServer(object):
    """Mock JamiQ server for testing the importer"""

    def __init__(self, data, testcase):
        self.data = data
        self.testcase = testcase

    def check_query(self, query):
        self.testcase.assertIn('filter_by', query)

        for i in ('topic_id', 'start_date', 'end_date',
                  'content_sentiment_score'):
            self.testcase.assertIn(i, query['filter_by'])

        self.testcase.assertIn('grouping', query)
        self.testcase.assertEqual(query['grouping'], {'by': 'content_date',
                                                      'gap': '+1day'})

        css = query['filter_by']['content_sentiment_score']
        self.testcase.assertEqual(len(css), 2)
        self.testcase.assertTrue((css[0].startswith('>=') and
                                  css[1].startswith('<=')) or
                                 (css[0].startswith('<=') and
                                  css[1].startswith('>=')))
        topic_id = query['filter_by']['topic_id']
        self.testcase.assertIsInstance(topic_id, list)
        self.testcase.assertEqual(len(topic_id), 1)

        start_date = iso8601.parse_date(query['filter_by']['start_date']) \
                            .date()
        end_date = iso8601.parse_date(query['filter_by']['end_date']) \
                          .date()

        self.testcase.assertGreaterEqual(end_date, start_date)

        # Each query must have a period of 10 years max
        self.testcase.assertLessEqual((end_date - start_date).days,
                                      365.25 * 10)

        return True

    def check_headers(self, headers):
        self.testcase.assertIn('Content-Type', headers)
        self.testcase.assertIn('Accept', headers)
        self.testcase.assertEqual(headers['Content-Type'], 'application/json')
        self.testcase.assertEqual(headers['Accept'], 'application/json')

        return True

    def query(self, query):
        start_date = iso8601.parse_date(
            query['filter_by']['start_date']).date()
        end_date = iso8601.parse_date(query['filter_by']['end_date']) \
                          .date()
        topic_id = query['filter_by']['topic_id'][0]
        sentiment_filter = query['filter_by']['content_sentiment_score']

        comparefn = {
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y
        }

        conditions = []
        for condition in sentiment_filter:
            sign, value = condition.split(' ')
            value = float(value)

            conditions.append((sign, value))

        filtered_data = itertools.ifilter(
            lambda dp: (dp['date'] >= start_date and
                        dp['date'] < end_date and
                        dp['topic_id'] == topic_id and
                        all(comparefn[c[0]](dp['value'], c[1])
                            for c in conditions)),
            self.data)

        padding = (
            {'date': start_date + datetime.timedelta(days),
             'count': 0}
            for days in xrange(0, (end_date - start_date).days)
        )

        padded_data = []
        value = None
        for i in filtered_data:
            if value is not None and i['date'] < value['date']:
                padded_data.append(i)
                padded_data.append(value)
                value = None

            for value in padding:
                if value['date'] < i['date']:
                    padded_data.append(value)
                else:
                    break

            padded_data.append(i)

        rest = padding if value is None else itertools.chain([value], padding)
        padded_data.extend(rest)

        return [
            [
                datetime.datetime.combine(
                    k, datetime.time(tzinfo=iso8601.UTC)
                ).isoformat(),
                sum(i['count'] for i in v)
            ]
            for k, v in itertools.groupby(padded_data,
                                          lambda dp: dp['date'])
        ]


class TestJamiqImporter(TestCase):
    auth = ('username', 'password')
    queryurl = 'https://localhost'
    data = 'TEST DATA'

    def setUp(self):
        # Add some chaff here to make sure the importer isn't just looking at
        # the first credential
        Credential.objects.create(username='foobar',
                                  password='barfoo')

        # Real credential
        self.credential = Credential.objects.create(username=self.auth[0],
                                                    password=self.auth[1])

        # Blank topic
        self.blanktopic = self.credential.topics.create(topic_id=1234)

        # Topic with two datapoints, out of order to make sure .latest() is
        # used
        self.filledtopic = self.credential.topics.create(topic_id=12345)
        self.filledtopic.datapoints.create(
            datestamp=datetime.date(2013, 1, 2),
            positive_sentiment_count=0,
            neutral_sentiment_count=0,
            negative_sentiment_count=5
        )
        self.filledtopic.datapoints.create(
            datestamp=datetime.date(2013, 1, 1),
            positive_sentiment_count=0,
            neutral_sentiment_count=0,
            negative_sentiment_count=6
        )

        d = datetime.date
        bid = self.blanktopic.topic_id
        fid = self.filledtopic.topic_id

        self.server = MockJamiqServer([
            dict(date=d(2013, 1, 1), value=-0.8, count=5, topic_id=bid),
            dict(date=d(2013, 1, 2), value=-0.5, count=5, topic_id=bid),
            dict(date=d(2013, 1, 3), value=-0.2, count=1, topic_id=bid),
            dict(date=d(2013, 1, 4), value=0, count=1, topic_id=bid),
            dict(date=d(2013, 1, 5), value=0.2, count=1, topic_id=bid),
            dict(date=d(2013, 1, 6), value=0.5, count=1, topic_id=bid),
            dict(date=d(2013, 1, 7), value=0.8, count=1, topic_id=bid),

            dict(date=d(2013, 1, 1), value=-0.8, count=6, topic_id=fid),
            dict(date=d(2013, 1, 2), value=-0.5, count=5, topic_id=fid),
            dict(date=d(2013, 1, 3), value=-0.2, count=1, topic_id=fid),
            dict(date=d(2013, 1, 4), value=0, count=1, topic_id=fid),
            dict(date=d(2013, 1, 5), value=0.2, count=1, topic_id=fid),
            dict(date=d(2013, 1, 6), value=0.5, count=1, topic_id=fid),
            dict(date=d(2013, 1, 7), value=0.8, count=1, topic_id=fid),
        ], self)

    def _get_importer(self, topic=None):
        topic = self.blanktopic if topic is None else topic
        return JamiqImporter(topic, self.queryurl)

    def _get_mock_postfn(self, mocker):
        postfn = mocker.replace('requests.post')
        response = mocker.mock()
        expect(postfn(self.queryurl,
                      data=simplejson.dumps(self.data),
                      headers=MATCH(self.server.check_headers),
                      verify=False,
                      auth=self.auth)) \
            .result(response)
        expect(postfn(ARGS, KWARGS)).count(0, 0)

        return postfn, response

    def test__perform_ok(self):
        importer = self._get_importer()
        mocker = Mocker()

        fakejson = {'results': None}

        postfn, response = self._get_mock_postfn(mocker)
        expect(response.status_code).result(200).count(1, None)
        expect(response.json()).result(fakejson)

        with mocker:
            self.assertIs(importer._perform(self.data), fakejson)

    def test__perform_error(self):
        importer = self._get_importer()
        mocker = Mocker()

        postfn, response = self._get_mock_postfn(mocker)
        expect(response.status_code).result(403).count(1, None)
        expect(response.text).result("error message").count(1, None)

        with mocker:
            with self.assertRaises(JamiqError):
                importer._perform(self.data)

    def _perform_test(self, topic):
        importer = JamiqImporter(topic, 'https://localhost')
        mocker = Mocker()

        process_request = lambda q: {'results': self.server.query(q)}

        mockimporter = mocker.patch(importer)
        expect(mockimporter._perform(MATCH(self.server.check_query))) \
            .count(1, None) \
            .call(process_request)
        expect(mockimporter._perform(ARGS, KWARGS)).count(0, 0)

        with mocker:
            importer.run()

        self.assertEqual(
            topic.datapoints.count(),
            (datetime.date.today() -
             topic.datapoints.order_by('datestamp')[0].datestamp).days
        )

        for dp in self.server.data:
            if dp['topic_id'] != topic.topic_id:
                continue

            djdp = topic.datapoints.get(datestamp=dp['date'])

            if dp['value'] >= 2.0 / 3 * 2 - 1:
                cls = 'positive'
            elif dp['value'] >= 2.0 / 3 - 1:
                cls = 'neutral'
            else:
                cls = 'negative'

            self.assertEqual(getattr(djdp, cls + '_sentiment_count'),
                             dp['count'])
            for k in {'positive', 'neutral', 'negative'} - {cls}:
                self.assertEqual(getattr(djdp, k + '_sentiment_count'), 0)

            return djdp

    def test_blanktopic_import(self):
        self._perform_test(self.blanktopic)

    def test_filledtopic_import(self):
        self._perform_test(self.filledtopic)


class TestJamiqTopicImporter(TransactionTestCase):
    queryurl = 'https://localhost'

    def setUp(self):
        self.credential = Credential.objects.create(username='foobar',
                                                    password='barfoo')

        self.credential.topics.create(topic_id=1, name='topic1')
        self.credential.topics.create(topic_id=2, name='topic2')

    def testImport(self):
        importer = JamiqTopicImporter(self.credential, self.queryurl)

        mocker = Mocker()
        getfn = mocker.replace('requests.get')
        response = mocker.mock()
        expect(getfn(self.queryurl,
                     headers={'Accept': 'application/json'},
                     verify=False,
                     auth=(self.credential.username,
                           self.credential.password))) \
            .result(response).count(1, None)
        expect(getfn(ARGS, KWARGS)).count(0, 0)

        expect(response.status_code).result(200).count(1, None)
        expect(response.json()).count(1, None).result({
            'result': [
                {'id': 2,
                 'topic': 'topic2NEW'},

                {'id': 3,
                 'topic': 'topic3'},

                {'id': 4,
                 'topic': 'topic4'}
            ]})

        with mocker:
            importer.run()

        self.assertEqual(self.credential.topics.get(topic_id=2).name,
                         'topic2NEW')
        self.assertEqual(self.credential.topics.get(topic_id=3).name,
                         'topic3')
        self.assertEqual(self.credential.topics.get(topic_id=4).name,
                         'topic4')

        with self.assertRaises(Topic.DoesNotExist):
            self.credential.topics.get(topic_id=1)


class JamiqTopicMatcherTest(TestCase):
    def setUp(self):
        c = Credential.objects.create(username='foobar', password='barfoo')
        self.topic1 = c.topics.create(topic_id=1, name='project1')
        self.topic2 = c.topics.create(topic_id=2, name='project2')
        self.invalid_topic = c.topics.create(topic_id=4, name='invalid')

        self.project1 = Project.objects.create(name='project1')
        self.project2 = Project.objects.create(name='project2')
        self.invalid_project = Project.objects.create(name='project4')

    def test_match_all(self):
        call_command('match_project_jamiqtopics')
        self.assertEqual(self.project1, self.topic1.jtp.get().project)
        self.assertEqual(self.project2, self.topic2.jtp.get().project)

        self.assertFalse(self.invalid_topic.jtp.exists())
        self.assertFalse(self.invalid_project.jtp.exists())

    def test_match_some(self):
        call_command('match_project_jamiqtopics',
                     self.topic1.id, self.topic2.id)

        self.assertEqual(self.project1, self.topic1.jtp.get().project)
        self.assertEqual(self.project2, self.topic2.jtp.get().project)

        self.assertFalse(self.invalid_topic.jtp.exists())
        self.assertFalse(self.invalid_project.jtp.exists())
