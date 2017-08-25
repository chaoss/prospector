# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Format'
        db.create_table(u'downloadinfo_format', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'downloadinfo', ['Format'])

        # Adding model 'DataSource'
        db.create_table(u'downloadinfo_datasource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('format', self.gf('django.db.models.fields.related.ForeignKey')(related_name='download_sources', to=orm['downloadinfo.Format'])),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('project', self.gf('mptt.fields.TreeForeignKey')(related_name='download_datasources', to=orm['projectinfo.Project'])),
        ))
        db.send_create_signal(u'downloadinfo', ['DataSource'])

        # Adding model 'DataPoint'
        db.create_table(u'downloadinfo_datapoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoints', to=orm['downloadinfo.DataSource'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('downloads', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'downloadinfo', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['source', 'date']
        db.create_unique(u'downloadinfo_datapoint', ['source_id', 'date'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataPoint', fields ['source', 'date']
        db.delete_unique(u'downloadinfo_datapoint', ['source_id', 'date'])

        # Deleting model 'Format'
        db.delete_table(u'downloadinfo_format')

        # Deleting model 'DataSource'
        db.delete_table(u'downloadinfo_datasource')

        # Deleting model 'DataPoint'
        db.delete_table(u'downloadinfo_datapoint')


    models = {
        u'downloadinfo.datapoint': {
            'Meta': {'unique_together': "(('source', 'date'),)", 'object_name': 'DataPoint'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'downloads': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoints'", 'to': u"orm['downloadinfo.DataSource']"})
        },
        u'downloadinfo.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'format': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'download_sources'", 'to': u"orm['downloadinfo.Format']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'download_datasources'", 'to': u"orm['projectinfo.Project']"}),
            'url': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'downloadinfo.format': {
            'Meta': {'object_name': 'Format'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'projectinfo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'projectinfo.license': {
            'Meta': {'object_name': 'License'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_osi_approved': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'projectinfo.project': {
            'Meta': {'object_name': 'Project'},
            'business_unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'projects'", 'null': 'True', 'to': u"orm['projectinfo.BusinessUnit']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'governance': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'has_contributor_agreement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_wip': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'projects'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['projectinfo.License']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['projectinfo.Project']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['downloadinfo']
