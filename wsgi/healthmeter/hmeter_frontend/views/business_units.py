# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.views.generic import TemplateView
import itertools

from healthmeter.utils import ProxyObject
from healthmeter.hmeter_frontend.models import Project, Metric
from healthmeter.projectinfo.models import BusinessUnit


class BusinessUnitIndex(TemplateView):
    template_name = 'hmeter_frontend/business-units.html'

    def get_context_data(self, **kwargs):
        data = super(BusinessUnitIndex, self).get_context_data(**kwargs)
        business_units = BusinessUnit.objects.prefetch_related('products')
        projects = Project.objects.filter(parent__isnull=True) \
                                  .order_by('business_unit') \
                                  .prefetch_dates() \
                                  .with_l1_scores()

        bu_index = dict(
            (buid, list(projs))
            for buid, projs in
            itertools.groupby(projects, lambda p: p.business_unit_id))

        data['descriptions'] = dict((project.id, project.description)
                                    for project in projects)

        def get_products(bu):
            # sort locally because of prefetch
            for product in sorted(bu.products.all(), key=lambda p: p.name):
                if product.name == 'JBoss BRMS':
                    yield ProxyObject(product,
                                      projects=bu_index.get(bu.id, None))
                else:
                    yield product

        data['business_units'] = [
            ProxyObject(bu,
                        root_projects=bu_index.get(bu.id, None),
                        products=get_products(bu))
            for bu in business_units
        ]
        data['unassociated_projects'] = bu_index[None]

        data['l1_metrics'] = Metric.objects.filter(level=1).order_by('lft')

        return data
