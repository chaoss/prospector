# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.views.generic import TemplateView
import random


class PageNotFoundView(TemplateView):
    template_name = '404.html'

    quotes = [
        "Your file was so big.\n"
        "It might be very useful.\n"
        "But now it is gone.\n"
        "-- David J. Liszewski",

        "The Web site you seek\n"
        "Cannot be located, but\n"
        "Countless more exist.",

        "Chaos reigns within.\n"
        "Reflect, repent, and reboot.\n"
        "Order shall return.\n"
        "-- Suzie Wagner",

        "Program aborting:\n"
        "Close all that you have worked on.\n"
        "You ask far too much.",

        "Windows NT crashed.\n"
        "I am the Blue Screen of Death.\n"
        "No one hears your screams.",

        "Yesterday it worked.\n"
        "Today it is not working.\n"
        "Windows is like that.",

        "First snow, then silence.\n"
        "This thousand-dollar screen dies\n"
        "So beautifully.",

        "With searching comes loss\n"
        "And the presence of absence:\n"
        '"My Novel" not found.',

        "The Tao that is seen\n"
        "Is not the true Tao until\n"
        "You bring fresh toner.",

        "Stay the patient course.\n"
        "Of little worth is your ire.\n"
        "The network is down.",

        "A crash reduces\n"
        "Your expensive computer\n"
        "To a simple stone.",

        "Three things are certain:\n"
        "Death, taxes and lost data.\n"
        "Guess which has occurred.",

        "You step in the stream,\n"
        "But the water has moved on.\n"
        "This page is not here.",

        "Out of memory.\n"
        "We wish to hold the whole sky,\n"
        "But we never will.",

        "Having been erased,\n"
        "The document you're seeking\n"
        "Must now be retyped.",

        "Serious error.\n"
        "All shortcuts have disappeared.\n"
        "Screen. Mind. Both are blank....",
    ]

    def get_context_data(self, **kwargs):
        data = super(PageNotFoundView, self).get_context_data(**kwargs)
        data['quote'] = self.quotes[random.randrange(0, len(self.quotes))]

        return data

    def render_to_response(self, *args, **kwargs):
        """Hack to pre-render the response before passing it back"""
        kwargs['status'] = 404
        response = super(PageNotFoundView, self).render_to_response(*args,
                                                                    **kwargs)
        response.render()
        return response
