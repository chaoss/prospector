# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db.models import Q
from django.dispatch import receiver
import logging

from healthmeter.importerutils.signals import import_finished
from healthmeter.hmeter_frontend.models import Project, MetricCache

logger = logging.getLogger(__name__)


@receiver(import_finished)
def invalidate_metrics(start, end, importer, **kwargs):
    projects = importer.object.get_projects()
    all_projects = Project.objects.filter(id__in=[p.id for p in projects]) \
                                  .get_ancestors()

    range_query = Q()

    if start is not None:
        if end is not None:
            range_query |= (Q(start__lte=start, end__gte=start) |
                            Q(start__lte=end, end__gte=end) |
                            Q(start__gte=start, end__lte=end) |
                            Q(start__isnull=True, end__gte=start) |
                            Q(end__isnull=True, start__lte=end))

        else:
            range_query |= Q(end__gte=start)

    else:
        if end is not None:
            range_query |= Q(start__lte=end)

    scores = MetricCache.objects.filter(Q(project__in=all_projects) &
                                        range_query)

    logger.info("Invalidating [%s] scores in range [%s, %s] for %s",
                scores.count(), start, end, list(all_projects))

    scores.update(is_dirty=True)
