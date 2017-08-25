# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Copy project information from mlinfo to hmeter_frontend"""
        "Write your forwards methods here."
        for ml in orm['mlinfo.MailingList'].objects \
                .filter(mailinglist=None):
            newml = orm['hmeter_frontend.MailingList'](
                mailinglist_ptr_id=ml)
            newml.__dict__.update(ml.__dict__)
            newml.save()

        for mlp in orm['mlinfo.MailingListProject'].objects.all():
            orm['hmeter_frontend.MailingListProject'].objects \
                .create(mailing_list=mlp.mailing_list.mailinglist,
                        project_id=mlp.project_id,
                        purpose=mlp.purpose)

    def backwards(self, orm):
        """Copy project information from hmeter_frontend back to mlinfo"""
        orm['mlinfo.MailingListProject'].objects.all().delete()

        for mlp in orm['hmeter_frontend.MailingListProject'].objects.all():
            orm['mlinfo.MailingListProject'].objects \
                .create(mailing_list=mlp.mailing_list.mailinglist_ptr,
                        project_id=mlp.project_id,
                        purpose=mlp.purpose)

    models = {
        'hmeter_frontend.blog': {
            'Meta': {'object_name': 'Blog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projectinfo.Project']"}),
            'rss_url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        'hmeter_frontend.blogpost': {
            'Meta': {'object_name': 'BlogPost'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['participantinfo.Participant']"}),
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.Blog']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'hmeter_frontend.bug': {
            'Meta': {'unique_together': "(('tracker_info', 'bug_id'),)", 'object_name': 'Bug'},
            'bug_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tracker_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': "orm['hmeter_frontend.BugTrackerProject']"})
        },
        'hmeter_frontend.bugcomment': {
            'Meta': {'unique_together': "(('bug', 'comment_id'),)", 'object_name': 'BugComment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['participantinfo.Participant']"}),
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['hmeter_frontend.Bug']"}),
            'comment_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'hmeter_frontend.bugtracker': {
            'Meta': {'object_name': 'BugTracker'},
            'baseurl': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'bt_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.BugTrackerType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['projectinfo.Project']", 'through': "orm['hmeter_frontend.BugTrackerProject']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'hmeter_frontend.bugtrackerproject': {
            'Meta': {'unique_together': "(('product', 'component', 'project', 'bug_tracker'),)", 'object_name': 'BugTrackerProject'},
            'bug_tracker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.BugTracker']"}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projectinfo.Project']"})
        },
        'hmeter_frontend.bugtrackertype': {
            'Meta': {'object_name': 'BugTrackerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'hmeter_frontend.event': {
            'Meta': {'object_name': 'Event'},
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projectinfo.Project']"})
        },
        'hmeter_frontend.ircchannel': {
            'Meta': {'unique_together': "(('server', 'name'),)", 'object_name': 'IrcChannel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_logs_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['projectinfo.Project']", 'symmetrical': 'False'}),
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
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projectinfo.Project']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mlinfo.Purpose']"})
        },
        'hmeter_frontend.vcsrepository': {
            'Meta': {'object_name': 'VCSRepository', '_ormbases': ['vcsinfo.Repository']},
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projectinfo.Project']"}),
            'repository_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['vcsinfo.Repository']", 'unique': 'True', 'primary_key': 'True'})
        },
        'mlinfo.mailinglist': {
            'Meta': {'object_name': 'MailingList'},
            'archive_url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'project': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['projectinfo.Project']", 'through': "orm['mlinfo.MailingListProject']", 'symmetrical': 'False'})
        },
        'mlinfo.mailinglistproject': {
            'Meta': {'ordering': "('project__name',)", 'unique_together': "(('project', 'purpose'),)", 'object_name': 'MailingListProject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old_mailinglistproject_set'", 'to': "orm['mlinfo.MailingList']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old_mailinglistproject_set'", 'to': "orm['projectinfo.Project']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old_mailinglistproject_set'", 'to': "orm['mlinfo.Purpose']"})
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
        'projectinfo.project': {
            'Meta': {'object_name': 'Project'},
            'governance': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
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
