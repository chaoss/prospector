# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ParticipantName'
        db.create_table(u'participantinfo_participantname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['participantinfo.Participant'])),
        ))
        db.send_create_signal(u'participantinfo', ['ParticipantName'])

        # Adding unique constraint on 'ParticipantName', fields ['name', 'participant']
        db.create_unique(u'participantinfo_participantname', ['name', 'participant_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ParticipantName', fields ['name', 'participant']
        db.delete_unique(u'participantinfo_participantname', ['name', 'participant_id'])

        # Deleting model 'ParticipantName'
        db.delete_table(u'participantinfo_participantname')


    models = {
        u'participantinfo.emailaddress': {
            'Meta': {'unique_together': "(('owner', 'localpart', 'domainpart'),)", 'object_name': 'EmailAddress'},
            'domainpart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'null': 'True', 'to': u"orm['participantinfo.EmailDomain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localpart': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_addresses'", 'to': u"orm['participantinfo.Participant']"})
        },
        u'participantinfo.emaildomain': {
            'Meta': {'ordering': "['domain']", 'object_name': 'EmailDomain'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'participantinfo.participantname': {
            'Meta': {'unique_together': "(('name', 'participant'),)", 'object_name': 'ParticipantName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['participantinfo.Participant']"})
        }
    }

    complete_apps = ['participantinfo']
