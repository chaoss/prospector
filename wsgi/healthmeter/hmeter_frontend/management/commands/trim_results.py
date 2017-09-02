# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max
import logging
from optparse import make_option

from healthmeter.hmeter_frontend.models import Project, MetricCache

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '[<project id>...]'
    help = 'Trim cached scores for each project.'

    def add_arguments(self, parser):
        parser.add_argument('project_ids', type=int, nargs='+')

        parser.add_argument('-d', '--days',
                            type=int, action="store",
                            dest="days", default=settings.METRIC_CACHE_LIMIT,
                            help="Number of days of cached scores to keep")

        parser.add_argument('-n', '--dry-run',
                            action="store_true",
                            dest="dry_run", default=False,
                            help="Dry run")

    def handle(self, *project_ids, **options):
        days = options['days']
        dry_run = options['dry_run']

        logger.info("Will trim each project cached scores to %s days", days)
        logger.info("Dry running" if dry_run else "Not dry running")

        filter_args = {}
        if project_ids:
            filter_args['id__in'] = project_ids

        projects = Project.objects \
                          .filter(**filter_args) \
                          .annotate(latest=Max('cached_scores__end'),
                                    total_scores=Count('cached_scores__id')) \
                          .exclude(latest__isnull=True)
        for project in projects:
            logger.info("Processing project [%s]", project)
            logger.info("Latest score is at [%s]", project.latest)

            earliest = project.latest - datetime.timedelta(days=days)
            logger.info("Will remove scores up to %s", earliest)

            delete_qs = project.cached_scores.filter(end__lte=earliest)
            delete_count = delete_qs.count()
            delete_qs.delete()
            remaining = project.total_scores - delete_count

            if dry_run:
                logger.info("Will delete %s scores from %s, leaving %s.",
                            delete_count, project, remaining)
            else:
                logger.info("Deleted %s scores from %s, leaving %s",
                            delete_count, project, remaining)
