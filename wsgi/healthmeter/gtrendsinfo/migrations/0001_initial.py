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
        db.create_table('gtrendsinfo_credential', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('healthmeter.fields.PlaintextPasswordField')(max_length=255)),
        ))
        db.send_create_signal('gtrendsinfo', ['Credential'])

        # Adding unique constraint on 'Credential', fields ['username', 'password']
        db.create_unique('gtrendsinfo_credential', ['username', 'password'])

        # Adding model 'Query'
        db.create_table('gtrendsinfo_query', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyword', self.gf('django.db.models.fields.CharField')(unique=True, max_length=300)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now=True, blank=True)),
        ))
        db.send_create_signal('gtrendsinfo', ['Query'])

        # Adding model 'DataPoint'
        db.create_table('gtrendsinfo_datapoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyword', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoints', to=orm['gtrendsinfo.Query'])),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('gtrendsinfo', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['keyword', 'start', 'end']
        db.create_unique('gtrendsinfo_datapoint', ['keyword_id', 'start', 'end'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataPoint', fields ['keyword', 'start', 'end']
        db.delete_unique('gtrendsinfo_datapoint', ['keyword_id', 'start', 'end'])

        # Removing unique constraint on 'Credential', fields ['username', 'password']
        db.delete_unique('gtrendsinfo_credential', ['username', 'password'])

        # Deleting model 'Credential'
        db.delete_table('gtrendsinfo_credential')

        # Deleting model 'Query'
        db.delete_table('gtrendsinfo_query')

        # Deleting model 'DataPoint'
        db.delete_table('gtrendsinfo_datapoint')


    models = {
        'gtrendsinfo.credential': {
            'Meta': {'unique_together': "(('username', 'password'),)", 'object_name': 'Credential'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('healthmeter.fields.PlaintextPasswordField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'gtrendsinfo.datapoint': {
            'Meta': {'unique_together': "(('keyword', 'start', 'end'),)", 'object_name': 'DataPoint'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoints'", 'to': "orm['gtrendsinfo.Query']"}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'gtrendsinfo.query': {
            'Meta': {'object_name': 'Query'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gtrendsinfo']
