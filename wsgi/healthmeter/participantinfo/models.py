# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django.db import models, transaction
from healthmeter import managers, utils
from healthmeter.projectinfo.decorators import resource


class Participant(models.Model):
    def __unicode__(self):
        try:
            return self.names.all()[:1][0].name

        except IndexError:
            return ''


class ParticipantName(models.Model):
    name = models.CharField(max_length=255)
    participant = models.ForeignKey(Participant, related_name='names')

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'participant')


class EmailDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    objects = managers.get_natural_key_manager('domain')

    class Meta:
        verbose_name = "Email Domain"
        ordering = ['domain']

    def __unicode__(self):
        return unicode(self.domain)


class EmailAddressManager(managers.NaturalKeyManagerBase,
                          managers.QuerySetManager):
    natural_key_columns = ('localpart', 'domainpart')


class EmailAddress(models.Model):
    owner = models.ForeignKey(Participant, related_name='email_addresses')
    localpart = models.CharField(max_length=255)
    domainpart = models.ForeignKey(EmailDomain, related_name='addresses',
                                   null=True)

    class Meta:
        unique_together = ('localpart', 'domainpart')
        verbose_name = "Email Address"
        verbose_name_plural = "Email Addresses"

    # Additional things to support a virtual address field
    objects = EmailAddressManager()

    def __init__(self, *args, **kwargs):
        self._filter_kwargs(kwargs, create=True)

        super(EmailAddress, self).__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, *args, **kwargs):
        kwargs2 = None

        if self.domainpart is not None and not self.domainpart_id:
            kwargs2 = kwargs.copy()
            kwargs2['force_insert'] = True

            self.domainpart.save(*args, **kwargs2)
            self.domainpart = EmailDomain.objects.get(id=self.domainpart.id)

        return super(EmailAddress, self).save(*args, **kwargs)

    class QuerySet(models.query.QuerySet):
        """Custom queryset that allows for querying by full address"""
        def filter(self, *args, **kwargs):
            self.model._filter_kwargs(kwargs, create=False)

            return super(EmailAddress.QuerySet, self).filter(*args, **kwargs)

    @property
    def address(self):
        """Convenience property to get full address"""
        if self.domainpart:
            return u'%s@%s' % (self.localpart, self.domainpart.domain)

        else:
            return unicode(self.localpart)

    def __unicode__(self):
        return self.address

    @staticmethod
    def _filter_kwargs(kwargs, create):
        """
        Provide support for translating some virtual fields:
         - address: Gets split into localpart and domainpart

        @arg kwargs List of keyword arguments. Will be translated
        @arg create If sub-objects should be created.
        """

        try:
            values = kwargs.pop('address').split('@', 1)
            kwargs['localpart'], domainpart = values

            if create:
                try:
                    kwargs['domainpart'] = EmailDomain.objects.get(
                        domain=domainpart)
                except EmailDomain.DoesNotExist:
                    kwargs['domainpart'] = EmailDomain(domain=domainpart)

            else:
                kwargs['domainpart__domain'] = domainpart

        except KeyError:
            # address not present. Don't modify kwargs
            pass

        except ValueError:      # invalid email address -- missing @
            assert len(values) == 1
            kwargs['localpart'], kwargs['domainpart'] = values[0], None
