# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (('hmeter_frontend', '0032_copy_mlinfo_projects.py'),)
    def forwards(self, orm):
        # Removing unique constraint on 'MailingListProject', fields ['project', 'purpose']
        db.delete_unique('mlinfo_mailinglistproject', ['project_id', 'purpose_id'])

        # Deleting model 'MailingListProject'
        db.delete_table('mlinfo_mailinglistproject')


    def backwards(self, orm):
        # Adding model 'MailingListProject'
        db.create_table('mlinfo_mailinglistproject', (
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projectinfo.Project'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mailing_list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mlinfo.MailingList'])),
            ('purpose', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mlinfo.Purpose'])),
        ))
        db.send_create_signal('mlinfo', ['MailingListProject'])

        # Adding unique constraint on 'MailingListProject', fields ['project', 'purpose']
        db.create_unique('mlinfo_mailinglistproject', ['project_id', 'purpose_id'])


    models = {
        'mlinfo.mailinglist': {
            'Meta': {'object_name': 'MailingList'},
            'archive_url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'})
        },
        'mlinfo.post': {
            'Meta': {'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['participantinfo.Participant']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_lists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mlinfo.MailingList']", 'symmetrical': 'False'}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_rel_+'", 'to': "orm['mlinfo.Post']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mlinfo.purpose': {
            'Meta': {'object_name': 'Purpose'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['mlinfo']
