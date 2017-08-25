# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from __future__ import print_function
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from healthmeter.btinfo.models import BugTracker


class Command(BaseCommand):
    args = '<bugtracker id>'
    help = """
Runs through the Github setup process for the bug tracker ID specified on the
command line.
    """

    def handle(self, btid, **kwargs):
        obj = BugTracker.objects.get(id=btid)

        if obj.username or obj.password:
            raise CommandError("Username or password already specified on "
                               "{0}".format(obj))

        print("Please insert your Github client ID and secret.\n"
              "You may obtain a pair at "
              "https://github.com/settings/applications/new")

        client_id = raw_input("Client ID: ")
        client_secret = raw_input("Client secret: ")

        username = raw_input("Github username: ")
        password = raw_input("Github password: ")

        print("Requesting OAUTH token...")
        response = requests.post('https://api.github.com/authorizations',
                                 auth=(username, password),
                                 data=json.dumps(
                                     {'client_id': client_id,
                                      'client_secret': client_secret,
                                      'note': 'Health meter issues importer'}))
        if response.status_code != 201:
            raise CommandError("Could not get OAUTH token",
                               response.headers, response.content)

        token = response.json()['token']
        print("Got token: {0}".format(token))

        # Github authorization uses basic http auth with
        # username:password = oauth:x-oauth-basic
        obj.username = token
        obj.password = 'x-oauth-basic'
        obj.save()
