# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    depends_on = (
        ('projectinfo', '0004_add_has_cla_flag'),
        ('gtrendsinfo', '0001_initial')
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        projects = orm['projectinfo.Project'].objects.filter(
            gtrends_queries__isnull=True)

        for project in projects:
            project.gtrends_queries.create(keyword=project.name)

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

    models = {
        'btinfo.bugnamespace': {
            'Meta': {'unique_together': "(('product', 'component', 'bug_tracker'),)", 'object_name': 'BugNamespace'},
            'bug_tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'namespaces'", 'to': "orm['btinfo.BugTracker']"}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'btinfo.bugtracker': {
            'Meta': {'object_name': 'BugTracker'},
            'baseurl': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'bt_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['btinfo.Type']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('healthmeter.fields.PlaintextPasswordField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'btinfo.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'cveinfo.product': {
            'Meta': {'unique_together': "(('vendor', 'product'),)", 'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100'}),
            'vendor': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100'})
        },
        'gtrendsinfo.query': {
            'Meta': {'object_name': 'Query'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        'hmeter_frontend.blog': {
            'Meta': {'object_name': 'Blog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'blogs'", 'to': "orm['projectinfo.Project']"}),
            'rss_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '255'})
        },
        'hmeter_frontend.blogpost': {
            'Meta': {'unique_together': "(('blog', 'guid'),)", 'object_name': 'BlogPost'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['participantinfo.Participant']", 'null': 'True'}),
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': "orm['hmeter_frontend.Blog']"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'})
        },
        'hmeter_frontend.bugnamespace': {
            'Meta': {'object_name': 'BugNamespace', '_ormbases': ['btinfo.BugNamespace']},
            'bugnamespace_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['btinfo.BugNamespace']", 'unique': 'True', 'primary_key': 'True'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'related_name': "'bug_trackers'", 'symmetrical': 'False', 'to': "orm['projectinfo.Project']"})
        },
        'hmeter_frontend.cpeproduct': {
            'Meta': {'object_name': 'CPEProduct', '_ormbases': ['cveinfo.Product']},
            'product_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cveinfo.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'to': "orm['projectinfo.Project']"})
        },
        'hmeter_frontend.event': {
            'Meta': {'object_name': 'Event'},
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'to': "orm['projectinfo.Project']"})
        },
        'hmeter_frontend.gtrendsquery': {
            'Meta': {'object_name': 'GTrendsQuery', '_ormbases': ['gtrendsinfo.Query']},
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'gtrends_queries'", 'to': "orm['projectinfo.Project']"}),
            'query_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gtrendsinfo.Query']", 'unique': 'True', 'primary_key': 'True'})
        },
        'hmeter_frontend.ircchannel': {
            'Meta': {'ordering': "('server__name', 'name')", 'unique_together': "(('server', 'name'),)", 'object_name': 'IrcChannel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_logs_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'irc_channels'", 'symmetrical': 'False', 'to': "orm['projectinfo.Project']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'channels'", 'to': "orm['hmeter_frontend.IrcServer']"})
        },
        'hmeter_frontend.irclogin': {
            'Meta': {'unique_together': "(('nickname', 'server'),)", 'object_name': 'IrcLogin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'irc_logins'", 'to': "orm['participantinfo.Participant']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.IrcServer']"})
        },
        'hmeter_frontend.ircmeeting': {
            'Meta': {'ordering': "['time_start']", 'unique_together': "(('channel', 'time_start'),)", 'object_name': 'IrcMeeting'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meetings'", 'to': "orm['hmeter_frontend.IrcChannel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_end': ('django.db.models.fields.DateTimeField', [], {}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'hmeter_frontend.ircmessage': {
            'Meta': {'object_name': 'IrcMessage'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.IrcLogin']"}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['hmeter_frontend.IrcChannel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'hmeter_frontend.ircserver': {
            'Meta': {'object_name': 'IrcServer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'hmeter_frontend.mailinglist': {
            'Meta': {'object_name': 'MailingList', '_ormbases': ['mlinfo.MailingList']},
            'mailinglist_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mlinfo.MailingList']", 'unique': 'True', 'primary_key': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mailing_lists'", 'symmetrical': 'False', 'through': "orm['hmeter_frontend.MailingListProject']", 'to': "orm['projectinfo.Project']"})
        },
        'hmeter_frontend.mailinglistproject': {
            'Meta': {'ordering': "('project__name',)", 'unique_together': "(('project', 'purpose'),)", 'object_name': 'MailingListProject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.MailingList']"}),
            'project': ('mptt.fields.TreeForeignKey', [], {'to': "orm['projectinfo.Project']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlinfo.Purpose']"})
        },
        'hmeter_frontend.metric': {
            'Meta': {'object_name': 'Metric'},
            'algorithm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.MetricAlgorithm']", 'null': 'True', 'blank': 'True'}),
            'colour': ('colorful.fields.RGBColorField', [], {'max_length': '7', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['hmeter_frontend.Metric']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sibling_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        'hmeter_frontend.metricalgorithm': {
            'Meta': {'object_name': 'MetricAlgorithm'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'hmeter_frontend.metricscoreconstants': {
            'Meta': {'object_name': 'MetricScoreConstants'},
            'green_score': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'red_score': ('django.db.models.fields.FloatField', [], {}),
            'ry_boundary': ('django.db.models.fields.FloatField', [], {}),
            'yellow_score': ('django.db.models.fields.FloatField', [], {}),
            'yg_boundary': ('django.db.models.fields.FloatField', [], {})
        },
        'hmeter_frontend.vcsrepository': {
            'Meta': {'object_name': 'VCSRepository', '_ormbases': ['vcsinfo.Repository']},
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'vcs_repositories'", 'to': "orm['projectinfo.Project']"}),
            'repository_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['vcsinfo.Repository']", 'unique': 'True', 'primary_key': 'True'})
        },
        'mlinfo.mailinglist': {
            'Meta': {'object_name': 'MailingList'},
            'archive_url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'})
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
        },
        'projectinfo.license': {
            'Meta': {'object_name': 'License'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_osi_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'projectinfo.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'governance': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'has_contributor_agreement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'projects'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['projectinfo.License']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['projectinfo.Project']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'vcsinfo.repository': {
            'Meta': {'object_name': 'Repository'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'repositories'", 'to': "orm['vcsinfo.Type']"}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10000'})
        },
        'vcsinfo.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['hmeter_frontend']
    symmetrical = True
