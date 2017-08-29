# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import collections
import datetime
from django.db.models.query import QuerySet
from django.db.models import Max, Min, Q
import itertools
import operator

from healthmeter.managers import QuerySetManager, ProxyTreeManager
from .utils.stats import max_or_none, min_or_none

from healthmeter.vcsinfo import models as vcsmodels
from healthmeter.mlinfo import models as mlmodels
from healthmeter.btinfo import models as btmodels
from healthmeter.bloginfo import models as blogmodels


DateData = collections.namedtuple('DateData',
                                  ['smart_start_date', 'last_activity'])


class ProjectQuerySet(QuerySet):
    def prefetch_dates(self):
        """
        Prefetch smart_start_date and last_activity for all projects in
        queryset.
        """
        # Handling non-root projects would increase the complexity
        # significantly, so don't bother for the time being.
        if any(proj.parent_id for proj in self):
            raise NotImplemented("Cannot prefetch dates for non-root projects")

        # First bulk fetch dates
        models = (
            (vcsmodels.Commit, 'repository__project'),
            (mlmodels.Post, 'mailing_lists__projects'),
            (btmodels.Comment, 'bug__tracker_info__projects'),
            (blogmodels.Post, 'blog__projects')
        )

        trees = [proj.tree_id for proj in self]

        dates = {}
        for model, relation in models:
            key = relation + '__tree_id'
            qs = model.objects.filter(**{key + '__in': trees}) \
                              .values_list(key) \
                              .annotate(lastact=Max('timestamp'),
                                        firstact=Min('timestamp')) \
                              .exclude(lastact=None, firstact=None)
            for tree, lastact, firstact in qs:
                # only consider vcs commits to mark the beginning of a project
                if model is not vcsmodels.Commit:
                    firstact = None

                try:
                    item = dates[tree]
                    lastact = max_or_none(item.last_activity, lastact)
                    firstact = min_or_none(item.smart_start_date, firstact)

                except KeyError:
                    pass

                dates[tree] = DateData(firstact, lastact)

        # Store them in _cached_dates property
        for project in self:
            startact, lastact = dates.get(project.tree_id, (None, None))
            startact = project.start_date or startact

            # smart_start_date should be a date, so coax to that type
            if type(startact) is datetime.datetime:
                startact = startact.date()

            self.model.smart_start_date.preseed_cache(project, startact)
            self.model.last_activity.preseed_cache(project, lastact)

        return self

    def with_l1_scores(self):
        """
        Annotate each project in queryset with l1 metric scores
        """
        from .models import MetricCache
        scores_qs = MetricCache.objects \
                               .filter(metric__level=1,
                                       project__in=self,
                                       end__isnull=True) \
                               .order_by('project__name', 'metric__lft')

        scores = dict((projid, list(mcs))
                      for projid, mcs in
                      itertools.groupby(scores_qs, lambda mc: mc.project_id))

        for project in self:
            project.l1_scores = scores.get(project.id, [])

        return self

    def get_descendants(self, include_self=True):
        """
        Gets a the MPTT descendants of a queryset
        Found and modified from
        http://stackoverflow.com/questions/5722767
        """
        filters = []
        for node in self.all():
            lft, rght = node.lft, node.rght
            if include_self:
                lft -= 1
                rght += 1

            filters.append(Q(tree_id=node.tree_id, lft__gt=lft, rght__lt=rght))

        q = reduce(operator.or_, filters)

        return self.model.objects.filter(q)

    def get_ancestors(self, include_self=True):
        """
        Gets the MPTT ancestors of a queryset. Adapted from get_descendants()
        """

        filters = []
        for node in self.all():
            lft, rght = node.lft, node.rght

            if include_self:
                lft += 1
                rght -= 1

            filters.append(Q(tree_id=node.tree_id, lft__lt=lft, rght__gt=rght))

        q = reduce(operator.or_, filters)

        return self.model.objects.filter(q)


class ProjectManager(QuerySetManager, ProxyTreeManager):
    """
    Placeholder manager for ProjectManager that subclasses both QuerySetManager
    and ProxyTreeManager.
    """
    pass
