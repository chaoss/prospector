# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from __future__ import print_function
from launchpadlib.credentials import Credentials
from launchpadlib.launchpad import Launchpad
from lazr.restfulclient.errors import HTTPError

from django.core.management.base import BaseCommand, CommandError
from healthmeter.btinfo.models import BugTracker


class Command(BaseCommand):
    args = '<bugtracker id>'
    help = "Authenticates and gets an access token for launchpad."

    def handle(self, btid, **kwargs):
        obj = BugTracker.objects.get(id=btid)

        # Ensure a proper username first
        if not obj.username:
            obj.username = 'prospector'
            obj.save()

        credentials = Credentials(obj.username)
        request_token_url = credentials.get_request_token(
            web_root="production")

        print("Please visit {0} to authorize Open Source Prospector to access "
              "Launchpad.net on your behalf.".format(request_token_url))

        while True:
            raw_input("Press [ENTER] when ready, or ^C to cancel.")

            try:
                credentials.exchange_request_token_for_access_token(
                    web_root="production")
                break

            except HTTPError:
                print("Could not obtain access token. Have you authenticated "
                      "yet?")

        print("Obtained oauth access token. Saving to database...")
        obj.password = credentials.serialize()
        obj.save()
