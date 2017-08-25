# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

#!/usr/bin/python

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'healthmeter.settings'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from healthmeter.hmeter_frontend.models import MailingList
from healthmeter.hmeter_frontend.importers import mailing_list

ml = MailingList.objects.filter(archive_url__startswith='nntp')[0]
importer = mailing_list.MailImporter.get_importer(ml.archive_url)

importer_instance = importer(ml)
importer_instance.run()
