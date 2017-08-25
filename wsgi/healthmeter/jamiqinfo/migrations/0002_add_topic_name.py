# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Topic.name'
        db.add_column('jamiqinfo_topic', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Topic.name'
        db.delete_column('jamiqinfo_topic', 'name')


    models = {
        'jamiqinfo.credential': {
            'Meta': {'unique_together': "(('username', 'password'),)", 'object_name': 'Credential'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('healthmeter.fields.PlaintextPasswordField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'jamiqinfo.datapoint': {
            'Meta': {'unique_together': "(('topic', 'datestamp'),)", 'object_name': 'DataPoint'},
            'datestamp': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'negative_sentiment_count': ('django.db.models.fields.IntegerField', [], {}),
            'neutral_sentiment_count': ('django.db.models.fields.IntegerField', [], {}),
            'positive_sentiment_count': ('django.db.models.fields.IntegerField', [], {}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoints'", 'to': "orm['jamiqinfo.Topic']"})
        },
        'jamiqinfo.topic': {
            'Meta': {'unique_together': "(('credential', 'topic_id'),)", 'object_name': 'Topic'},
            'credential': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['jamiqinfo.Credential']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'topic_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['jamiqinfo']
