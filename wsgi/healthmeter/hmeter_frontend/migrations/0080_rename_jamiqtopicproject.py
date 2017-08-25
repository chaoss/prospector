# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'JamiqTopicProject', fields ['project', 'jamiqtopic']
        db.delete_unique(u'hmeter_frontend_jamiqtopicproject',
                         ['project_id', 'jamiqtopic_id'])

        # Renaming model 'JamiqTopicProject'
        db.rename_table(u'hmeter_frontend_jamiqtopicproject',
                        u'jamiqinfo_topic_projects')

        db.send_create_signal(u'jamiqinfo', ['Topic_Projects'])

        # Rename topic fk column name
        db.rename_column(u'jamiqinfo_topic_projects',
                         'jamiqtopic_id', 'topic_id')

        # Re-create unique constraint in jamiqinfo
        db.create_unique(u'jamiqinfo_topic_projects',
                         ['project_id', 'topic_id'])


    def backwards(self, orm):
        db.delete_unique('jamiqinfo_topic_projects',
                         ['project_id', 'topic_id'])

        db.rename_column('jamiqinfo_topic_projects',
                         'topic_id', 'jamiqtopic_id')

        db.rename_table(u'jamiqinfo_topic_projects',
                        u'hmeter_frontend_jamiqtopicproject')

        db.send_create_signal(u'hmeter_frontend', ['JamiqTopicProject'])

        # Re-add unique constraint on 'JamiqTopicProject',
        # fields ['project', 'jamiqtopic']
        db.create_unique(u'hmeter_frontend_jamiqtopicproject',
                         ['project_id', 'jamiqtopic_id'])


    models = {
        u'hmeter_frontend.blog': {
            'Meta': {'object_name': 'Blog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'blogs'", 'to': u"orm['projectinfo.Project']"}),
            'rss_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '255'})
        },
        u'hmeter_frontend.blogpost': {
            'Meta': {'unique_together': "(('blog', 'guid'),)", 'object_name': 'BlogPost'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['participantinfo.Participant']", 'null': 'True'}),
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': u"orm['hmeter_frontend.Blog']"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'})
        },
        u'hmeter_frontend.event': {
            'Meta': {'object_name': 'Event'},
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['projectinfo.Project']"})
        },
        u'hmeter_frontend.ircchannel': {
            'Meta': {'ordering': "('server__name', 'name')", 'unique_together': "(('server', 'name'),)", 'object_name': 'IrcChannel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'meeting_logs_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'related_name': "'irc_channels'", 'symmetrical': 'False', 'to': u"orm['projectinfo.Project']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'channels'", 'to': u"orm['hmeter_frontend.IrcServer']"})
        },
        u'hmeter_frontend.irclogin': {
            'Meta': {'unique_together': "(('nickname', 'server'),)", 'object_name': 'IrcLogin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'irc_logins'", 'to': u"orm['participantinfo.Participant']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hmeter_frontend.IrcServer']"})
        },
        u'hmeter_frontend.ircmeeting': {
            'Meta': {'ordering': "['time_start']", 'unique_together': "(('channel', 'time_start'),)", 'object_name': 'IrcMeeting'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meetings'", 'to': u"orm['hmeter_frontend.IrcChannel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_end': ('django.db.models.fields.DateTimeField', [], {}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'hmeter_frontend.ircmessage': {
            'Meta': {'object_name': 'IrcMessage'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hmeter_frontend.IrcLogin']"}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['hmeter_frontend.IrcChannel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'hmeter_frontend.ircserver': {
            'Meta': {'object_name': 'IrcServer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'hmeter_frontend.metric': {
            'Meta': {'object_name': 'Metric'},
            'algorithm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hmeter_frontend.MetricAlgorithm']", 'null': 'True', 'blank': 'True'}),
            'colour': ('colorful.fields.RGBColorField', [], {'max_length': '7', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['hmeter_frontend.Metric']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sibling_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'time_based': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hmeter_frontend.metricalgorithm': {
            'Meta': {'object_name': 'MetricAlgorithm'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'hmeter_frontend.metriccache': {
            'Meta': {'unique_together': "(('project', 'metric', 'start', 'end'),)", 'object_name': 'MetricCache'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {}),
            'metric': ('mptt.fields.TreeForeignKey', [], {'related_name': "'cached_scores'", 'to': u"orm['hmeter_frontend.Metric']"}),
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'cached_scores'", 'to': u"orm['projectinfo.Project']"}),
            'raw_value': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'hmeter_frontend.metricscoreconstants': {
            'Meta': {'object_name': 'MetricScoreConstants'},
            'green_score': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'red_score': ('django.db.models.fields.FloatField', [], {}),
            'ry_boundary': ('django.db.models.fields.FloatField', [], {}),
            'yellow_score': ('django.db.models.fields.FloatField', [], {}),
            'yg_boundary': ('django.db.models.fields.FloatField', [], {})
        },
        u'hmeter_frontend.options': {
            'Meta': {'object_name': 'Options', '_ormbases': [u'preferences.Preferences']},
            'highlight_domain': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['participantinfo.EmailDomain']", 'null': 'True'}),
            u'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'})
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
        u'preferences.preferences': {
            'Meta': {'object_name': 'Preferences'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sites.Site']", 'null': 'True', 'blank': 'True'})
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
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['hmeter_frontend']
