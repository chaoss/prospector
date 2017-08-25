# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import simplejson
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def jsonify(obj):
    return mark_safe(simplejson.dumps(obj))
