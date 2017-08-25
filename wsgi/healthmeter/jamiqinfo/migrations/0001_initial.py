# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Credential'
        db.create_table('jamiqinfo_credential', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('healthmeter.fields.PlaintextPasswordField')(max_length=255)),
        ))
        db.send_create_signal('jamiqinfo', ['Credential'])

        # Adding unique constraint on 'Credential', fields ['username', 'password']
        db.create_unique('jamiqinfo_credential', ['username', 'password'])

        # Adding model 'Topic'
        db.create_table('jamiqinfo_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('credential', self.gf('django.db.models.fields.related.ForeignKey')(related_name='topics', to=orm['jamiqinfo.Credential'])),
            ('topic_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('jamiqinfo', ['Topic'])

        # Adding unique constraint on 'Topic', fields ['credential', 'topic_id']
        db.create_unique('jamiqinfo_topic', ['credential_id', 'topic_id'])

        # Adding model 'DataPoint'
        db.create_table('jamiqinfo_datapoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoints', to=orm['jamiqinfo.Topic'])),
            ('datestamp', self.gf('django.db.models.fields.DateField')()),
            ('positive_sentiment_count', self.gf('django.db.models.fields.IntegerField')()),
            ('neutral_sentiment_count', self.gf('django.db.models.fields.IntegerField')()),
            ('negative_sentiment_count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('jamiqinfo', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['topic', 'datestamp']
        db.create_unique('jamiqinfo_datapoint', ['topic_id', 'datestamp'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataPoint', fields ['topic', 'datestamp']
        db.delete_unique('jamiqinfo_datapoint', ['topic_id', 'datestamp'])

        # Removing unique constraint on 'Topic', fields ['credential', 'topic_id']
        db.delete_unique('jamiqinfo_topic', ['credential_id', 'topic_id'])

        # Removing unique constraint on 'Credential', fields ['username', 'password']
        db.delete_unique('jamiqinfo_credential', ['username', 'password'])

        # Deleting model 'Credential'
        db.delete_table('jamiqinfo_credential')

        # Deleting model 'Topic'
        db.delete_table('jamiqinfo_topic')

        # Deleting model 'DataPoint'
        db.delete_table('jamiqinfo_datapoint')


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
            'topic_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['jamiqinfo']
