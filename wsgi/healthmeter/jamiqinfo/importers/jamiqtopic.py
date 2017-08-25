# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import transaction
import logging
import requests
import simplejson

from healthmeter.importerutils.importers import ImporterBase
from .jamiq import JamiqError

logger = logging.getLogger(__name__)


class JamiqTopicImporter(ImporterBase):
    def __init__(self, credential,
                 queryurl='https://api.jamiq.com/buzz/v2/topic'):
        super(JamiqTopicImporter, self).__init__(credential)
        self.queryurl = queryurl

    @transaction.commit_on_success
    def _run(self):
        headers = {'Accept': 'application/json'}
        response = requests.get(self.queryurl, headers=headers,
                                verify=False,
                                auth=(self.object.username,
                                      self.object.password))

        if response.status_code != 200:
            try:
                error = response.json()['errors']
            except:
                error = response.text

            raise JamiqError(error)

        result = response.json()['result']
        for topic in result:
            djtopic, created = self.object.topics.get_or_create(
                topic_id=topic['id'],
                defaults={'name': topic['topic']}
            )

            logger.info('%s topic [%s]',
                        'Imported' if created else 'Found', djtopic)

            if not created:
                djtopic.name = topic['topic']
                djtopic.save()

        topic_ids = [x['id'] for x in result]
        self.object.topics.exclude(topic_id__in=topic_ids).delete()

    @classmethod
    def resolve_importer_type(cls, obj):
        return 'jamiqtopic'


JamiqTopicImporter.register_importer('jamiqtopic', JamiqTopicImporter)
