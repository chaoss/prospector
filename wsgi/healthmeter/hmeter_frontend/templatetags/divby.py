# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django import template

register = template.Library()


@register.filter
def divby(dividend, divisor):
    return dividend / divisor
