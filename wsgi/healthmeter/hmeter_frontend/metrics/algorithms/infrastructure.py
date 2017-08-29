# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from .base import MetricAlgorithm
from .normalizers import BoolNormalizer
from .mixins import NullChecker

from ..lookup import metric

import healthmeter.projectinfo.models as projectmodels


@metric
class HasWebsite(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return bool(self.project.website_url)


@metric
class HasMailingList(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return self.project.all_mailing_lists.exists()


@metric
class HasDescription(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return bool(self.project.description)


@metric
class CLAAbsent(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return not self.project.has_contributor_agreement


@metric
class HasOSIApprovedLicense(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    @property
    def licenses(self):
        return projectmodels.License.objects.filter(projects__in=self.projects)

    def get_raw_value(self):
        return self.licenses.filter(is_osi_approved=True).exists()


@metric
class HasBugTracker(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return self.project.all_bug_trackers.exists()


@metric
class HasGovernanceModel(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return bool(self.project.governance)


@metric
class HasVcs(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return self.project.all_vcs_repositories.exists()


@metric
class HasBlog(NullChecker, MetricAlgorithm):
    normalizer = BoolNormalizer()

    def get_raw_value(self):
        return self.project.all_blogs.exists()
