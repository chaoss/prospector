# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'EmailAddress', fields ['owner', 'domainpart', 'localpart']
        db.create_unique('participantinfo_emailaddress', ['owner_id', 'domainpart_id', 'localpart'])


    def backwards(self, orm):
        # Removing unique constraint on 'EmailAddress', fields ['owner', 'domainpart', 'localpart']
        db.delete_unique('participantinfo_emailaddress', ['owner_id', 'domainpart_id', 'localpart'])


    models = {
        'participantinfo.emailaddress': {
            'Meta': {'unique_together': "(('owner', 'localpart', 'domainpart'),)", 'object_name': 'EmailAddress'},
            'domainpart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': "orm['participantinfo.EmailDomain']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localpart': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_addresses'", 'to': "orm['participantinfo.Participant']"})
        },
        'participantinfo.emaildomain': {
            'Meta': {'object_name': 'EmailDomain'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['participantinfo']
