# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    """Empty migration that re-freezes models with Topic_Projects added in"""

    depends_on = (
        ('hmeter_frontend', '0080_rename_jamiqtopicproject.py'),
    )

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {
        u'jamiqinfo.credential': {
            'Meta': {'unique_together': "(('username', 'password'),)", 'object_name': 'Credential'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('healthmeter.fields.PlaintextPasswordField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'jamiqinfo.datapoint': {
            'Meta': {'unique_together': "(('topic', 'datestamp'),)", 'object_name': 'DataPoint'},
            'datestamp': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'negative_sentiment_count': ('django.db.models.fields.IntegerField', [], {}),
            'neutral_sentiment_count': ('django.db.models.fields.IntegerField', [], {}),
            'positive_sentiment_count': ('django.db.models.fields.IntegerField', [], {}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoints'", 'to': u"orm['jamiqinfo.Topic']"})
        },
        u'jamiqinfo.topic': {
            'Meta': {'unique_together': "(('credential', 'topic_id'),)", 'object_name': 'Topic'},
            'credential': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': u"orm['jamiqinfo.Credential']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'related_name': "'jamiq_topics'", 'symmetrical': 'False', 'through': u"orm['jamiqinfo.Topic_Projects']", 'to': u"orm['projectinfo.Project']"}),
            'topic_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jamiqinfo.topic_projects': {
            'Meta': {'unique_together': "(('project', 'topic'),)", 'object_name': 'Topic_Projects'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['projectinfo.Project']"}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jamiqinfo.Topic']"})
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

    complete_apps = ['jamiqinfo']
