# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
Tests for participantinfo app
"""

from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from .models import *


class TestParticipant(TestCase):
    name = 'test'

    def test_create(self):
        """
        Test to ensure that creation of multiple participants with the same
        name works
        """
        participant = Participant.objects.create(name=self.name)
        participant2 = Participant.objects.create(name=self.name)

        self.assertNotEqual(participant.id, participant2.id)

    def test_unicode(self):
        participant = Participant.objects.create(name=self.name)

        self.assertEqual(unicode(participant), self.name)


class TestEmailDomain(TestCase):
    domain = 'example.com'

    def test_create(self):
        """
        Test to ensure that duplicate EmailDomain objects can't exist
        """
        EmailDomain.objects.create(domain=self.domain)

        with self.assertRaises(IntegrityError):
            EmailDomain.objects.create(domain=self.domain)

    def test_non_null(self):
        with self.assertRaises(IntegrityError):
            EmailDomain.objects.create(domain=None)

    def test_unicode(self):
        e = EmailDomain.objects.create(domain=self.domain)

        self.assertEqual(unicode(e), self.domain)
        self.assertEqual(e.domain, self.domain)


class TestEmailAddress(TransactionTestCase):
    name = 'test'
    othername = 'other test'

    localpart = 'test'
    domainpart = 'example.com'
    email = 'test@example.com'

    otherdomainpart = 'other.com'
    otheremail = 'test@other.com'

    def test_create_normal(self):
        participant = Participant.objects.create(name=self.name)

        emailobj = EmailAddress.objects.create(
            owner=participant,
            localpart=self.localpart,
            domainpart=EmailDomain.objects.create(domain=self.domainpart))

        self.assertEqual(unicode(emailobj), self.email)
        self.assertEqual(emailobj.address, self.email)

    def test_address_attribute(self):
        participant = Participant.objects.create(name=self.name)

        emailobj = EmailAddress.objects.create(owner=participant,
                                               address=self.email)

        self.assertEqual(emailobj,
                         EmailAddress.objects.get(address=self.email))

        emailobj2, created = \
            EmailAddress.objects.get_or_create(owner=participant,
                                               address=self.email)

        self.assertEqual(emailobj, emailobj2)
        self.assertFalse(created)

    def test_duplicate_address(self):
        participant = Participant.objects.create(name=self.name)
        EmailAddress.objects.create(owner=participant,
                                    address=self.email)
        # TODO: This section can be re-enabled when we properly normalize
        # EmailAddress.
        # with self.assertRaises(IntegrityError):
        #     EmailAddress.objects.create(owner=participant,
        #                                 address=self.email)

        # # Ensure we don't hit DatabaseError due to a terminated transaction
        # EmailAddress.objects.get(address=self.email)

    def test_multiple_addresses(self):
        participant = Participant.objects.create(name=self.name)
        e1 = EmailAddress.objects.create(owner=participant, address=self.email)
        e2 = EmailAddress.objects.create(owner=participant,
                                         address=self.otheremail)

        self.assertEqual(e1, EmailAddress.objects.get(address=self.email))
        self.assertEqual(e2, EmailAddress.objects.get(address=self.otheremail))
        self.assertNotEqual(e1, e2)

    def test_create_with_participant(self):
        email = EmailAddress.objects.create(owner_name=self.name,
                                            address=self.email)
        self.assertEqual(email.owner.name, self.name)
        self.assertEqual(email, EmailAddress.objects.get(address=self.email,
                                                         owner_name=self.name))

        email2, created = EmailAddress.objects.get_or_create(
            owner_name=self.name,
            address=self.email)
        self.assertFalse(created)
        self.assertEqual(email, email2)
        self.assertEqual(Participant.objects.filter(name=self.name).count(), 1)

        # TODO: This section can be re-enabled when we properly normalize
        # EmailAddress
        # with self.assertRaises(IntegrityError):
        #     EmailAddress.objects.create(owner_name=self.name,
        #                                 address=self.email)

    def test_multiple_names(self):
        email = EmailAddress.objects.create(owner_name=self.name,
                                            address=self.email)
        email2, created = EmailAddress.objects.get_or_create(
            owner_name=self.othername,
            address=self.email)

        self.assertTrue(created)
        self.assertNotEqual(email, email2)
