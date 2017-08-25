# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import transaction
from django.core.exceptions import MultipleObjectsReturned
import email.utils
from healthmeter.participantinfo.models import Participant, EmailAddress

import logging

logger = logging.getLogger(__name__)


@transaction.atomic
def get_participant(name, email):
    """
    name: String containing name of participant
    email: String containing email of participant

    Get hmeter_frontend.models.Participant object or create one with
    corresponding ParticipantEmail
    """
    if not email:
        try:
            return Participant.objects \
                              .filter(names__name=name,
                                      email_addresses__isnull=True)[:1][0]

        except IndexError:
            part = Participant.objects.create()
            part.names.create(name=name)
            return part

    try:
        return EmailAddress.objects.get(address=email).owner

    except EmailAddress.DoesNotExist:
        part = Participant.objects.create()
        part.names.create(name=name)
        EmailAddress.objects.create(address=email, owner=part)
        return part

    except MultipleObjectsReturned:
        logger.warn("Multiple email addresses found matching %s. "
                    "Refining query to include name.. (%s, %s)", email,
                    name, email,
                    exc_info=True)

        return EmailAddress.objects.filter(
            address=email, owner__names__name=name)[:1][0]


def undo_antispam_mangling(email):
    """
    Undo antispam mangling, e.g. foo@domain.com -> foo at domain.com
    @arg email Mangled email address
    @return Unmangled email address
    """
    for pattern in [' at ', '_at_', ' en ', '<at>', ' <at> ']:
        if pattern in email:
            email = email.replace(pattern, '@')
            break

    return email.replace(' dot ', '.')


def parseaddr(addrstring):
    """
    Like email.utils.parseaddr, but with a workaround for broken parsing of
    invalid emails.
    """
    name, email_ = email.utils.parseaddr(addrstring)

    # HACK: Workaround email.utils.parseaddr broken parsing of foo
    # <bar@baz.(none)> as ('foo (none)', 'bar@baz.')
    if (addrstring.endswith('(none)>') and name.endswith(' (none)')
            and email_.endswith('.')):
        name = name[:-len(' (none)')]
        email_ += '(none)'

    return (name, email_)


__all__ = ['get_participant', 'undo_antispam_mangling', 'parseaddr']
