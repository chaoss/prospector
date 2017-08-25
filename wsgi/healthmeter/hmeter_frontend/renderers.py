# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django_medusa.log import get_logger
from django_medusa.renderers import StaticSiteRenderer
from django.core.urlresolvers import normalize, reverse, NoReverseMatch
from django.conf import settings
from django.db import connection
from django.db.utils import InterfaceError
from preferences import preferences
from .models import Project
from .urls import project_urlpatterns
from .utils.containers import filterdict


class ProjectRenderer(StaticSiteRenderer):
    @staticmethod
    def get_paths_for_project(project_id):
        paths = set()

        proj_views = [
            ('hmeter_frontend:project:' + urlpat.name,
             normalize(urlpat.regex.pattern))
            for urlpat in project_urlpatterns
        ]

        # paths.add(proj.get_absolute_url())
        default_kwargs = {'id': project_id,
                          'pk': project_id,
                          'domain': ''}
        hldomain = getattr(preferences.Options.highlight_domain,
                           'domain', '')

        for name, possibilities in proj_views:
            for _, keys in possibilities:
                kwargs = filterdict(default_kwargs, whitelist=keys)

                try:
                    paths.add(reverse(name, kwargs=kwargs))
                except NoReverseMatch:
                    pass

                # Also request one for hldomain if domain is a keyword here
                if 'domain' in keys:
                    kwargs['domain'] = hldomain
                    try:
                        paths.add(reverse(name, kwargs=kwargs))
                    except NoReverseMatch:
                        pass

        return paths

    def get_paths(self):
        paths = set([reverse('hmeter_frontend:project:index'),
                     reverse('hmeter_frontend:business_units'),
                     reverse('hmeter_frontend:all_projects'),
                     reverse('hmeter_frontend:about'),
                     reverse('hmeter_frontend:contact')])
        proj_views = [
            ('hmeter_frontend:project:' + urlpat.name,
             normalize(urlpat.regex.pattern))
            for urlpat in project_urlpatterns
        ]

        for proj in Project.objects.root_nodes():
            paths |= self.get_paths_for_project(proj.id)

        return sorted(paths)

    def render_path(self, *args, **kwargs):
        # Retry after an InterfaceError
        max_attempts = 5
        for i in xrange(max_attempts):
            try:
                return super(ProjectRenderer, self).render_path(*args,
                                                                **kwargs)

            except InterfaceError, e:
                self.logger.warn("Caught InterfaceError, closing connection "
                                 "and trying again (attempt #%s)",
                                 i, exc_info=True)
                try:
                    connection.close()
                except:
                    pass

        self.logger.error("Failed to render page after %s attempts. "
                          "Re-raising last exception...", max_attempts)
        raise e

    def generate(self):
        if getattr(settings, 'MEDUSA_MULTITHREAD', False):
            connection.close()

        super(ProjectRenderer, self).generate()


class ManualRenderer(ProjectRenderer):
    """
    Medusa renderer that supplies paths based on what's passed to the
    constructor.
    """
    def __init__(self, paths):
        self.__paths = paths
        super(ManualRenderer, self).__init__()

    def get_paths(self):
        return self.__paths


renderers = [ProjectRenderer]
