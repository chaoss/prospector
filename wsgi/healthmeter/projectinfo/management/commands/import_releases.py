# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import dateutil.parser
from django.core.management.base import BaseCommand, CommandError
import logging
from optparse import make_option

from healthmeter.projectinfo.models import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--project', '-p',
                    dest='project',
                    help='Project ID to import releases for'),
    )

    args = '[<FILE>...]'

    help = """Import releases from <FILE>s. <FILE> should be a text file in the
following format, where each <date> has the format dd/mm/yyyy:

<date> <release>
<date> <release>"""

    def handle(self, *args, **options):
        if 'project' not in options:
            raise CommandError("Project ID not provided.")

        project = Project.objects.get(id=options['project'])

        logger.debug("Project is %s", project)

        for filename in args:
            logger.debug("Opening file %s", filename)

            with open(filename) as f:
                for line in f:
                    date_str, version = line.strip().split(' ', 1)
                    date = dateutil.parser.parse(date_str)

                    release, created = project.releases \
                                              .get_or_create(version=version,
                                                             defaults={
                                                                 'date': date
                                                             })

                    logger.info("%s version %s",
                                "Imported" if created else "Found",
                                release)

                    if not created:
                        release.date = date
                        release.save()
