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

        # Adding model 'Participant'
        db.create_table('healthmeter_participant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('hmeter_frontend', ['Participant'])

        # Adding model 'ParticipantEmail'
        db.create_table('healthmeter_participantemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.Participant'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('hmeter_frontend', ['ParticipantEmail'])

        # Adding model 'Project'
        db.create_table('healthmeter_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['healthmeter.Project'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('hmeter_frontend', ['Project'])

        # Adding model 'VCSType'
        db.create_table('healthmeter_vcstype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('hmeter_frontend', ['VCSType'])

        # Adding model 'VCSRepository'
        db.create_table('healthmeter_vcsrepository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.Project'])),
            ('vcs_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.VCSType'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal('hmeter_frontend', ['VCSRepository'])

        # Adding model 'VCSCommit'
        db.create_table('healthmeter_vcscommit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.VCSRepository'])),
            ('commit_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.Participant'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('hmeter_frontend', ['VCSCommit'])

        # Adding unique constraint on 'VCSCommit', fields ['repository', 'commit_id']
        db.create_unique('healthmeter_vcscommit', ['repository_id', 'commit_id'])

        # Adding model 'MailingListPurpose'
        db.create_table('healthmeter_mailinglistpurpose', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('hmeter_frontend', ['MailingListPurpose'])

        # Adding model 'MailingList'
        db.create_table('healthmeter_mailinglist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('posting_address', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('archive_url', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal('hmeter_frontend', ['MailingList'])

        # Adding model 'MailingListProject'
        db.create_table('healthmeter_mailinglistproject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mailing_list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.MailingList'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.Project'])),
            ('purpose', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.MailingListPurpose'])),
        ))
        db.send_create_signal('hmeter_frontend', ['MailingListProject'])

        # Adding unique constraint on 'MailingListProject', fields ['project', 'purpose']
        db.create_unique('healthmeter_mailinglistproject', ['project_id', 'purpose_id'])

        # Adding model 'MailingListPost'
        db.create_table('healthmeter_mailinglistpost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['healthmeter.Participant'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('message_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('hmeter_frontend', ['MailingListPost'])

        # Adding M2M table for field mailing_lists on 'MailingListPost'
        db.create_table('healthmeter_mailinglistpost_mailing_lists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglistpost', models.ForeignKey(orm['healthmeter.mailinglistpost'], null=False)),
            ('mailinglist', models.ForeignKey(orm['healthmeter.mailinglist'], null=False))
        ))
        db.create_unique('healthmeter_mailinglistpost_mailing_lists', ['mailinglistpost_id', 'mailinglist_id'])

        # Adding M2M table for field references on 'MailingListPost'
        db.create_table('healthmeter_mailinglistpost_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_mailinglistpost', models.ForeignKey(orm['healthmeter.mailinglistpost'], null=False)),
            ('to_mailinglistpost', models.ForeignKey(orm['healthmeter.mailinglistpost'], null=False))
        ))
        db.create_unique('healthmeter_mailinglistpost_references', ['from_mailinglistpost_id', 'to_mailinglistpost_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'MailingListProject', fields ['project', 'purpose']
        db.delete_unique('healthmeter_mailinglistproject', ['project_id', 'purpose_id'])

        # Removing unique constraint on 'VCSCommit', fields ['repository', 'commit_id']
        db.delete_unique('healthmeter_vcscommit', ['repository_id', 'commit_id'])

        # Deleting model 'Participant'
        db.delete_table('healthmeter_participant')

        # Deleting model 'ParticipantEmail'
        db.delete_table('healthmeter_participantemail')

        # Deleting model 'Project'
        db.delete_table('healthmeter_project')

        # Deleting model 'VCSType'
        db.delete_table('healthmeter_vcstype')

        # Deleting model 'VCSRepository'
        db.delete_table('healthmeter_vcsrepository')

        # Deleting model 'VCSCommit'
        db.delete_table('healthmeter_vcscommit')

        # Deleting model 'MailingListPurpose'
        db.delete_table('healthmeter_mailinglistpurpose')

        # Deleting model 'MailingList'
        db.delete_table('healthmeter_mailinglist')

        # Deleting model 'MailingListProject'
        db.delete_table('healthmeter_mailinglistproject')

        # Deleting model 'MailingListPost'
        db.delete_table('healthmeter_mailinglistpost')

        # Removing M2M table for field mailing_lists on 'MailingListPost'
        db.delete_table('healthmeter_mailinglistpost_mailing_lists')

        # Removing M2M table for field references on 'MailingListPost'
        db.delete_table('healthmeter_mailinglistpost_references')


    models = {
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
