# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from healthmeter.hmeter_frontend.migration_utils import was_applied

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        if was_applied(__file__, 'healthmeter'):
            return
        # Changing field 'BugTracker.username'
        db.alter_column('healthmeter_bugtracker', 'username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'BugTracker.password'
        db.alter_column('healthmeter_bugtracker', 'password', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))


    def backwards(self, orm):
        
        # Changing field 'BugTracker.username'
        db.alter_column('healthmeter_bugtracker', 'username', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'BugTracker.password'
        db.alter_column('healthmeter_bugtracker', 'password', self.gf('django.db.models.fields.CharField')(default='', max_length=255))


    models = {
        'healthmeter.bug': {
            'Meta': {'unique_together': "(('tracker_info', 'bug_id'),)", 'object_name': 'Bug'},
            'bug_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tracker_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': "orm['healthmeter.BugTrackerProject']"})
        },
        'healthmeter.bugcomment': {
            'Meta': {'unique_together': "(('bug', 'comment_id'),)", 'object_name': 'BugComment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Bug']"}),
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['healthmeter.Bug']"}),
            'comment_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'healthmeter.bugtracker': {
            'Meta': {'object_name': 'BugTracker'},
            'baseurl': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'bt_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.BugTrackerType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['healthmeter.Project']", 'through': "orm['healthmeter.BugTrackerProject']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'healthmeter.bugtrackerproject': {
            'Meta': {'unique_together': "(('project', 'product', 'component'),)", 'object_name': 'BugTrackerProject'},
            'bug_tracker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.BugTracker']"}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Project']", 'unique': 'True'})
        },
        'healthmeter.bugtrackertype': {
            'Meta': {'object_name': 'BugTrackerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'healthmeter.mailinglist': {
            'Meta': {'object_name': 'MailingList'},
            'archive_url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'project': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['healthmeter.Project']", 'through': "orm['healthmeter.MailingListProject']", 'symmetrical': 'False'})
        },
        'healthmeter.mailinglistpost': {
            'Meta': {'object_name': 'MailingListPost'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Participant']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_lists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['healthmeter.MailingList']", 'symmetrical': 'False'}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_rel_+'", 'to': "orm['healthmeter.MailingListPost']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'healthmeter.mailinglistproject': {
            'Meta': {'ordering': "('project__name',)", 'unique_together': "(('project', 'purpose'),)", 'object_name': 'MailingListProject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.MailingList']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Project']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.MailingListPurpose']"})
        },
        'healthmeter.mailinglistpurpose': {
            'Meta': {'object_name': 'MailingListPurpose'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'healthmeter.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'healthmeter.participantemail': {
            'Meta': {'object_name': 'ParticipantEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Participant']"})
        },
        'healthmeter.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['healthmeter.Project']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'healthmeter.vcscommit': {
            'Meta': {'unique_together': "(('repository', 'commit_id'),)", 'object_name': 'VCSCommit'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Participant']"}),
            'commit_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.VCSRepository']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'healthmeter.vcsrepository': {
            'Meta': {'object_name': 'VCSRepository'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.Project']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'vcs_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['healthmeter.VCSType']"})
        },
        'healthmeter.vcstype': {
            'Meta': {'object_name': 'VCSType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['healthmeter']
