# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('hmeter_frontend', '0023_move_participantinfo_tables_out.py'),
    )

    def forwards(self, orm):
        db.rename_column('participantinfo_emailaddress',
                         'email_local', 'localpart')
        db.rename_column('participantinfo_emailaddress',
                         'email_domain_id', 'domainpart_id')
        db.rename_column('participantinfo_emailaddress',
                         'participant_id', 'owner_id')


    def backwards(self, orm):
        db.rename_column('participantinfo_emailaddress',
                         'localpart', 'email_local')
        db.rename_column('participantinfo_emailaddress',
                         'domainpart_id', 'email_domain_id')
        db.rename_column('participantinfo_emailaddress',
                         'owner_id', 'participant_id')

    models = {
        'participantinfo.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
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
