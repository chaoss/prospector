# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.management.base import BaseCommand, CommandError
from healthmeter.projectinfo.models import Project
from healthmeter.jamiqinfo.models import Topic

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '[<id>...]'
    help = """
Associates jamiqinfo.Topic objects with Project objects when their names match.
If <id>... is specified, then only Topic's of the given <id>s are processed.
Otherwise, all Topic objects are processed.
    """

    def handle(self, *args, **kwargs):
        qs = Topic.objects.filter(projects__isnull=True)

        if args:
            qs = qs.filter(id__in=args)

        for topic in qs.iterator():
            try:
                project = Project.objects.get(name=topic.name)
                jtp = topic.projects.add(project)

                logger.info("Associated %s with %s", topic, project)

            except Project.DoesNotExist:
                logger.warn("Skipped %s: No project with matching name.",
                            topic)
