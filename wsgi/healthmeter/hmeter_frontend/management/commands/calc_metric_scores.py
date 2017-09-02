# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from healthmeter.hmeter_frontend.models import Project, MetricCache, Metric
from healthmeter.hmeter_frontend.metrics.calc import calc_score
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<project id> [<max days>]'
    help = 'Populates the MetricCache model with historical metric information'

    def add_arguments(self, parser):
        parser.add_argument('projectid', type=int)

        parser.add_argument('maxdays',
                            action="store", type=int, nargs='?',
                            default=settings.METRIC_CACHE_LIMIT,
                            help="Max days")

        parser.add_argument('-f', '--flush',
                            action="store_true",
                            dest="flush", default=False,
                            help="Flush cache")

    def iterdays(self, maxdays, project_start):
        """
        Iterate from maxdays before today or project_start until today,
        whichever yields the smaller range.
        """
        today = datetime.datetime.combine(datetime.date.today(),
                                          datetime.time())
        d = (today - datetime.timedelta(days=int(maxdays))
             if maxdays is not None
             else project_start)

        dates = [x for x in [d, project_start] if x is not None]

        if not dates:
            raise CommandError("Project start date is unknown. "
                               "Specify a number of days to go back to.")

        d = max(dates)

        oneday = datetime.timedelta(days=1)
        while d < today:
            yield d
            d += oneday

    @classmethod
    def unset_date(cls, result):
        """Recursively set date of all nodes in result to None"""
        for child in result.children:
            cls.unset_date(child)

        result.end = None
        result.id = None

    def handle(self, projectid, maxdays=None, **options):
        project = Project.objects.get(id=projectid)
        metric = Metric.objects.root_nodes()[:1][0]

        all_metrics = MetricCache.objects.filter(
            project=project,
            metric__in=metric.get_descendants(include_self=True))

        if options['flush']:
            clean_days = set()
        else:
            clean_days = set(all_metrics.filter(is_dirty=False,
                                                start__isnull=True)
                             .values_list('end', flat=True))

        smart_start_date = project.smart_start_date
        start_date = (None if smart_start_date is None else
                      datetime.datetime.combine(project.smart_start_date,
                                                datetime.time()))

        for d in self.iterdays(maxdays, start_date):
            if d not in clean_days:
                result = calc_score(project, metric, None, d)

                with transaction.atomic():
                    result.save_all()

        latest_score = project.cached_scores \
                              .filter(metric__parent__isnull=True,
                                      end__isnull=False) \
                              .latest('end')

        logger.info("Setting score for [%s - %s] as the latest score",
                    latest_score.start, latest_score.end)

        self.unset_date(latest_score)
        latest_score.save_all()
