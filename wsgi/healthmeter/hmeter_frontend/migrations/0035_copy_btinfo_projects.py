# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Move project relation into hmeter_frontend.BugNamespace"""
        for bns in orm['btinfo.BugNamespace'].objects \
                .distinct('product', 'component', 'bug_tracker'):
            try:
                newbns = orm['hmeter_frontend.BugNamespace'].objects \
                    .get(product=bns.product,
                         component=bns.component,
                         bug_tracker_id=bns.bug_tracker_id)

            except orm['hmeter_frontend.BugNamespace'].DoesNotExist:
                newbns = orm['hmeter_frontend.BugNamespace'](
                    bugnamespace_ptr=bns)
                newbns.__dict__.update(bns.__dict__)
                newbns.save()

                for bns in orm['btinfo.BugNamespace'].objects \
                    .filter(bug_tracker_id=bns.bug_tracker_id,
                            product=bns.product,
                            component=bns.component):

                    # Avoid fetching too many fields -- will break if
                    # projectinfo migrations haven't applied yet
                    project = orm['projectinfo.Project'].objects \
                        .only('id') \
                        .get(id=bns.project_id)

                    newbns.projects.add(project)

        # Delete duplicate bugnamespaces once we're done here
        orm['btinfo.BugNamespace'].objects.filter(bugnamespace=None).delete()

    def backwards(self, orm):
        """Move project relation back into btinfo.BugNamespace"""
        for bns in orm['hmeter_frontend.BugNamespace'].objects.all():
            for project in bns.projects.all():
                if project == bns.project:
                    continue

                orm['btinfo.BugNamespace'].objects.get_or_create(
                    project=project,
                    product=bns.product,
                    component=bns.component,
                    bug_tracker_id=bns.bug_tracker_id)

    models = {
        'btinfo.bugnamespace': {
            'Meta': {'unique_together': "(('product', 'component', 'bug_tracker', 'project'),)", 'object_name': 'BugNamespace'},
            'bug_tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'namespaces'", 'to': "orm['btinfo.BugTracker']"}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projectinfo.Project']"})
        },
        'btinfo.bugtracker': {
            'Meta': {'object_name': 'BugTracker'},
            'baseurl': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'bt_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['btinfo.Type']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'btinfo.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
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
        'hmeter_frontend.bugnamespace': {
            'Meta': {'object_name': 'BugNamespace', '_ormbases': ['btinfo.BugNamespace']},
            'bugnamespace_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['btinfo.BugNamespace']", 'unique': 'True', 'primary_key': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bug_trackers'", 'symmetrical': 'False', 'to': "orm['projectinfo.Project']"})
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
