# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Renaming model 'EmailDomain'
        db.rename_table('hmeter_frontend_emaildomain',
                        'participantinfo_emaildomain')

        # Renaming model 'ParticipantEmail'
        db.rename_table('hmeter_frontend_participantemail',
                        'participantinfo_emailaddress')

        # Renaming model 'Participant'
        db.rename_table('hmeter_frontend_participant',
                        'participantinfo_participant')


        # Changing field 'VCSCommit.author'
        db.alter_column('hmeter_frontend_vcscommit', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['participantinfo.Participant']))

        # Changing field 'IrcLogin.participant'
        db.alter_column('hmeter_frontend_irclogin', 'participant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['participantinfo.Participant']))

        # Changing field 'BugComment.author'
        db.alter_column('hmeter_frontend_bugcomment', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['participantinfo.Participant']))

        # Changing field 'MailingListPost.author'
        db.alter_column('hmeter_frontend_mailinglistpost', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['participantinfo.Participant']))

        # Changing field 'BlogPost.author'
        db.alter_column('hmeter_frontend_blogpost', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['participantinfo.Participant']))

        if not db.dry_run:
            ContentType.objects \
                .filter(app_label='hmeter_frontend',
                        model__in=('emaildomain', 'participant')) \
                .update(app_label='vcsinfo')

            ContentType.objects \
                .filter(app_label='hmeter_frontend', model='participantemail') \
                .update(app_label='vcsinfo', model='emailaddress')

    def backwards(self, orm):
        # Renaming model 'EmailDomain'
        db.rename_table('participantinfo_emaildomain',
                        'hmeter_frontend_emaildomain')

        # Renaming model 'ParticipantEmail'
        db.rename_table('participantinfo_emailaddress',
                        'hmeter_frontend_participantemail')

        # Renaming model 'Participant'
        db.rename_table('participantinfo_participant',
                        'hmeter_frontend_participant')

        # Changing field 'VCSCommit.author'
        db.alter_column('hmeter_frontend_vcscommit', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hmeter_frontend.Participant']))

        # Changing field 'IrcLogin.participant'
        db.alter_column('hmeter_frontend_irclogin', 'participant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hmeter_frontend.Participant']))

        # Changing field 'BugComment.author'
        db.alter_column('hmeter_frontend_bugcomment', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hmeter_frontend.Participant']))

        # Changing field 'MailingListPost.author'
        db.alter_column('hmeter_frontend_mailinglistpost', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hmeter_frontend.Participant']))

        # Changing field 'BlogPost.author'
        db.alter_column('hmeter_frontend_blogpost', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hmeter_frontend.Participant']))

        if not db.dry_run:
            ContentType.objects \
                .filter(app_label='vcsinfo',
                        model__in=('emaildomain', 'participant')) \
                .update(app_label='hmeter_frontend')

            ContentType.objects \
                .filter(app_label='vcsinfo', model='emailaddress') \
                .update(app_label='hmeter_frontend', model='participantemail')

    models = {
        'hmeter_frontend.blog': {
            'Meta': {'object_name': 'Blog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.Project']"}),
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
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hmeter_frontend.Project']", 'through': "orm['hmeter_frontend.BugTrackerProject']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'hmeter_frontend.bugtrackerproject': {
            'Meta': {'unique_together': "(('product', 'component', 'project', 'bug_tracker'),)", 'object_name': 'BugTrackerProject'},
            'bug_tracker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.BugTracker']"}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.Project']"})
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
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.Project']"})
        },
        'hmeter_frontend.ircchannel': {
            'Meta': {'unique_together': "(('server', 'name'),)", 'object_name': 'IrcChannel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_logs_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hmeter_frontend.Project']", 'symmetrical': 'False'}),
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
            'Meta': {'object_name': 'MailingList'},
            'archive_url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'project': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hmeter_frontend.Project']", 'through': "orm['hmeter_frontend.MailingListProject']", 'symmetrical': 'False'})
        },
        'hmeter_frontend.mailinglistpost': {
            'Meta': {'object_name': 'MailingListPost'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['participantinfo.Participant']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_lists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hmeter_frontend.MailingList']", 'symmetrical': 'False'}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_rel_+'", 'to': "orm['hmeter_frontend.MailingListPost']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'hmeter_frontend.mailinglistproject': {
            'Meta': {'ordering': "('project__name',)", 'unique_together': "(('project', 'purpose'),)", 'object_name': 'MailingListProject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.MailingList']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.Project']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.MailingListPurpose']"})
        },
        'hmeter_frontend.mailinglistpurpose': {
            'Meta': {'object_name': 'MailingListPurpose'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'hmeter_frontend.project': {
            'Meta': {'object_name': 'Project'},
            'governance': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['hmeter_frontend.Project']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'hmeter_frontend.projectrelease': {
            'Meta': {'ordering': "('date', 'version')", 'unique_together': "(('project', 'version'),)", 'object_name': 'ProjectRelease'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['hmeter_frontend.Project']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hmeter_frontend.vcscommit': {
            'Meta': {'unique_together': "(('repository', 'commit_id'),)", 'object_name': 'VCSCommit'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['participantinfo.Participant']"}),
            'commit_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.VCSRepository']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'hmeter_frontend.vcsrepository': {
            'Meta': {'object_name': 'VCSRepository'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.Project']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'vcs_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmeter_frontend.VCSType']"})
        },
        'hmeter_frontend.vcstype': {
            'Meta': {'object_name': 'VCSType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['hmeter_frontend']
