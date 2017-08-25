# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Query.last_updated'
        db.alter_column('gtrendsinfo_query', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'Query.last_updated'
        db.alter_column('gtrendsinfo_query', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

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
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gtrendsinfo']
