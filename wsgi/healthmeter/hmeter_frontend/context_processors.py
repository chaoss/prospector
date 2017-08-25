# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from .forms import FeedbackForm


def feedback_form(context):
    if 'feedback_form' in context:
        return {}

    return {
        'feedback_form': FeedbackForm()
    }
