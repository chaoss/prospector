# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import groupby
import json

from django.conf import settings
from django.db.models import Count, Sum
from django.views.generic import DetailView

from healthmeter.hmeter_frontend import models
from ...metrics.constants import get_score_constants
from ...utils.cache import (djcached, cached_property,
                            project_cache_key_template)

from healthmeter.btinfo import models as btmodels
from healthmeter.mlinfo import models as mlmodels
from healthmeter.vcsinfo import models as vcsmodels


class ProjectDetail(DetailView):
    template_name = 'hmeter_frontend/project/detail.html'
    context_object_name = 'project'
    model = models.Project

    month_periods = (3, 6, 9, 12, 24)

    @cached_property
    def projects(self):
        return self.object.all_projects

    @cached_property
    def repositories(self):
        return self.object.all_vcs_repositories.select_related('type') \
                                               .order_by('type__name')

    @cached_property
    def commits(self):
        return vcsmodels.Commit.objects \
                               .filter(repository__in=self.repositories)

    @cached_property
    def bug_namespaces(self):
        return self.object.all_bug_trackers.all() \
                          #.prefetch_related('bug_tracker__bt_type__name')

    @cached_property
    def bugs(self):
        return btmodels.Bug.objects \
                           .filter(tracker_info__in=self.bug_namespaces)

    @cached_property
    def bug_comments(self):
        return btmodels.Comment.objects \
                               .filter(bug__in=self.bugs)

    @cached_property
    def mailing_lists(self):
        return self.object.all_mailing_lists \
                          .order_by('posting_address') \
                          .distinct()

    @cached_property
    def posts(self):
        return mlmodels.Post.objects \
                            .filter(mailing_lists__in=self.mailing_lists)

    @cached_property
    def blogs(self):
        return self.object.all_blogs

    @cached_property
    def limits(self):
        today = datetime.utcnow()
        return [(x, (today - relativedelta(months=x)))
                for x in self.month_periods]

    @staticmethod
    def gen_type_with_count(iterable):
        return ["%s(%d)" % (key, len(list(group)))
                for key, group in groupby(iterable)]

    def gen_periodic_data(self, *fns):
        return [
            [months] + [fn(limit) for fn in fns]
            for months, limit in self.limits
        ]

    def populate_vcsdata(self):
        repositories = self.repositories
        self.data['vcs_repository_types'] = self.gen_type_with_count(
            x.type.name for x in repositories)

        self.data['vcs_repository_urls'] = [x.url for x in repositories]

        commits = self.commits
        self.data['commit_count_period'] = self.gen_periodic_data(
            lambda limit: commits.filter(timestamp__gte=limit).count(),
            lambda limit: (commits.filter(timestamp__gte=limit)
                           .distinct('author').count()))

        head_commits = commits.filter()
        current_sloc = (head_commits.aggregate(sloc=Sum('line_count'))['sloc']
                        or 0)
        ancestors_lists = []
        sloc_count_period = self.data['sloc_count_period'] = []
        for months, limit in self.limits:
            total_sloc_at_limit = 0
            for ancestors in ancestors_lists:
                if not ancestors:
                    continue
                try:
                    sloc_at_limit = vcsmodels.Commit.objects \
                        .filter(id__in=ancestors, timestamp__gte=limit) \
                        .order_by('timestamp')[:1][0].line_count

                except IndexError:
                    # no commits later than limit, so pick latest commit
                    try:
                        sloc_at_limit = vcsmodels.Commit.objects \
                                                 .filter(id__in=ancestors) \
                                                 .latest('timestamp') \
                                                 .line_count
                    except:
                        continue

                total_sloc_at_limit += sloc_at_limit
            sloc_count_period.append([months,
                                      current_sloc - total_sloc_at_limit])

        committer_domains = models.EmailDomain.objects \
            .filter(addresses__owner__committer_ids__commits__in=commits) \
            .with_commit_count() \
            .filter(commit_count__gt=0)

        self.data['commit_domain_breakdown'] = [
            (x['domain'], x['commit_count'], x['address_count'])
            for x in committer_domains
        ]

    def populate_releases(self):
        try:
            self.data['latest_release'] = self.object.all_releases \
                                                     .order_by('-date')[:1][0]
        except IndexError:
            pass

    def populate_btdata(self):
        bugnamespaces = self.bug_namespaces

        self.data['bug_tracker_types'] = self.gen_type_with_count(
            x.bug_tracker.bt_type.name for x in bugnamespaces)

        self.data['bug_tracker_namespaces'] = list(bugnamespaces)

        # Subquery needed to avoid capturing comments 2..N, because we only
        # want the first comment of each bug.
        firstcomments = btmodels.Comment.objects.filter(
            id__in=self.bug_comments.distinct('bug'))
        bugs = self.bugs

        self.data['bugs_opened_count_period'] = self.gen_periodic_data(
            lambda limit: firstcomments.filter(timestamp__gte=limit).count())
        self.data['severe_bugs_count_period'] = self.gen_periodic_data(
            lambda limit: firstcomments.filter(
                timestamp__gte=limit,
                bug__severity__level__gte=3).count())
        self.data['bugs_closed_count_period'] = self.gen_periodic_data(
            lambda limit: bugs.filter(close_date__gte=limit).count())

        domains = models.EmailDomain.objects \
            .filter(addresses__owner__bug_comments__in=firstcomments) \
            .with_btcomment_count() \
            .filter(btcomment_count__gt=0)
        self.data['bug_reports_domain_breakdown'] = [
            (x['domain'], x['btcomment_count'], x['address_count'])
            for x in domains
        ]

    def populate_mldata(self):
        mailing_lists = self.mailing_lists
        self.data['mailing_lists'] = mailing_lists
        self.data['mailing_list_count'] = len(mailing_lists)

        posts = self.posts
        self.data['mail_count_period'] = self.gen_periodic_data(
            lambda limit: posts.filter(timestamp__gte=limit).count(),
            lambda limit: (posts.filter(timestamp__gte=limit)
                           .distinct('author').count()))

        domains = models.EmailDomain.objects \
            .filter(addresses__owner__mailing_list_posts__in=posts) \
            .with_mlpost_count() \
            .filter(mlpost_count__gt=0)
        self.data['mlpost_domain_breakdown'] = [
            (x['domain'], x['mlpost_count'], x['address_count'])
            for x in domains
        ]

    def populate_miscdata(self):
        self.data['start_date'] = self.object.smart_start_date
        self.data['end_date'] = self.object.last_updated
        self.data['hldomain'] = ''

    def _populate_listdata_with_count(self, basename, items):
        self.data[basename + 's'] = items
        self.data[basename + '_count'] = len(items)

    def populate_blogdata(self):
        self._populate_listdata_with_count('blog', self.blogs)

    def populate_metricinfo(self):
        score_constants = get_score_constants()

        self.data['metric_score_constants'] = json.dumps({
            'yg_boundary': score_constants.yg_boundary,
            'ry_boundary': score_constants.ry_boundary
        })

        # TODO: Pull this out of MetricCache instead
        self.data['score_tree'] = self.object.score

    def __gen_detail_cache_key(self):
        return project_cache_key_template.format(id=self.object.id,
                                                 key='detail_data')

    @djcached(__gen_detail_cache_key, 24 * 3600)
    def get_projdata(self):
        self.data = {
            'project': self.object,
            'subprojects_count': self.projects.count() - 1,
            'pending_subprojects_count': 0,  # FIXME
        }

        self.populate_releases()
        self.populate_vcsdata()
        self.populate_btdata()
        self.populate_mldata()
        self.populate_miscdata()
        self.populate_blogdata()
        self.populate_metricinfo()

        return self.data

    def get_context_data(self, **kwargs):
        data = super(ProjectDetail, self).get_context_data(**kwargs)
        data.update(self.get_projdata())

        return data
