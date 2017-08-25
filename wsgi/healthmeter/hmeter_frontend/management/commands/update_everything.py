# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings

from collections import defaultdict
import logging
import multiprocessing
import signal
import threading

from healthmeter.importerutils.mptasks import ImporterTask
from healthmeter.hmeter_frontend.models import Project
from healthmeter.projectinfo.resources import get_resource_models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '[<project id>...]'
    help = 'Updates and recalculates scores for the project ids provided'

    def handle(self, *projectids, **options):
        projects = (Project.objects.filter(parent__isnull=True)
                    if not projectids else
                    Project.objects.filter(id__in=projectids))

        all_projects = projects.get_descendants(include_self=True)
        resources = set()
        project_deps = defaultdict(set)
        project_deps_lock = threading.Lock()
        calculating_projects = set()

        # SIGUSR1 -- state dump
        def dump_status(*args):
            logger.info("Remaining importers: %s", project_deps)
            logger.info("Remaining projects for calculation: %s",
                        calculating_projects)

        signal.signal(signal.SIGUSR1, dump_status)

        # Collect set of resources
        for res_model in get_resource_models():
            project_attr, _ = res_model.get_project_field()
            opts = {
                project_attr + '__in': all_projects
            }
            for resource in res_model.objects.filter(**opts):
                resources.add(resource)
                for project in resource.get_projects():
                    project_deps[project.get_root().id].add(resource)

        # finish import handler, and autostart calc_metric_scores
        def finish_import(resource):
            with project_deps_lock:
                try:
                    logger.info("Finished importing resource [%s]", resource)

                    projects = set(proj.get_root() for proj in
                                   resource.get_projects())

                    for project in projects:
                        logger.info("Removing [%s] from [%s] dependencies",
                                    resource, project)
                        remaining = project_deps[project.id]
                        assert(remaining)
                        remaining.remove(resource)

                        logger.info("Remaining dependencies for project [%s] "
                                    "are: %s",
                                    project, remaining)

                        if not remaining:
                            pool.apply_async(RecalcTask(project),
                                             callback=gen_finish_calc(project))
                            del project_deps[project.id]
                except:
                    logger.critical("Error in finish_import!!!",
                                    exc_info=True)

        def finish_calc(project):
            try:
                calculating_projects.remove(project)
                logger.info("Finished calculating project %s. Remaining: %s",
                            project, calculating_projects)
            except:
                pass

        def gen_finish_import_cb(resource):
            return lambda _: finish_import(resource)

        def gen_finish_calc(project):
            return lambda _: finish_calc(project)

        # Run through importers
        connection.close()
        pool = multiprocessing.Pool(getattr(settings, 'IMPORTER_CONCURRENCY',
                                            multiprocessing.cpu_count()))

        promises = [
            pool.apply_async(ImporterTask(resource),
                             callback=gen_finish_import_cb(resource))
            for resource in resources
        ]

        # Wait until all of the above are done before closing, because
        # finish_import adds more tasks
        for promise in promises:
            promise.wait(365 * 24 * 3600)
        pool.close()
        pool.join()

        # We should have finished everything at this point.
        assert(not project_deps)


class RecalcTask(object):
    def __init__(self, project):
        self.project = project

    def __call__(self):
        try:
            logger.info("Beginning calculation of metric scores for %s",
                        self.project)
            call_command('calc_metric_scores', self.project.id,
                         settings.METRIC_CACHE_LIMIT)
            call_command('trim_results', self.project.id)

        except:
            logger.error("Could not recalculate metric scores for [%s]",
                         self.project, exc_info=True)
