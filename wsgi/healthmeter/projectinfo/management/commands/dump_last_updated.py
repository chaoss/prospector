# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.core.management.base import BaseCommand, CommandError
from healthmeter.projectinfo.models import Project
from healthmeter.projectinfo.resources import get_resource_models


class Command(BaseCommand):
    args = '[<projid>....]'

    def handle(self, *args, **options):
        projects = (Project.objects.filter(id__in=args) if args else
                    Project.objects.root_nodes()).order_by('name')
        res_models = list(sorted(get_resource_models(),
                                 key=lambda r: r._meta.verbose_name))

        for project in projects.iterator():
            print u'{0}:'.format(project.name)
            for res_model in res_models:
                project_attr, is_m2m = res_model.get_project_field()
                kwargs = {
                    project_attr + '__in': project.get_descendants(
                        include_self=True)
                }

                res_instances = list(res_model.objects.filter(**kwargs))

                if res_instances:
                    print u' - {0}:'.format(
                        res_model._meta.verbose_name_plural)

                for inst in res_instances:
                    print u'   - {inst}: {last_updated}'.format(
                        inst=inst,
                        last_updated=getattr(inst, 'last_updated', 'Unknown')
                    )

            # empty line after each project
            print ''
