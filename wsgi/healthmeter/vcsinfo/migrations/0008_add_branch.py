# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Branch'
        db.create_table('vcsinfo_branch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('latest_commit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='commits', to=orm['vcsinfo.Commit'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('vcsinfo', ['Branch'])


    def backwards(self, orm):
        # Deleting model 'Branch'
        db.delete_table('vcsinfo_branch')


    models = {
        'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'vcsinfo.branch': {
            'Meta': {'object_name': 'Branch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_commit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['vcsinfo.Commit']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'vcsinfo.commit': {
            'Meta': {'unique_together': "(('repository', 'commit_id'),)", 'object_name': 'Commit'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['participantinfo.Participant']"}),
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'_parents'", 'to': "orm['vcsinfo.Commit']", 'through': "orm['vcsinfo.CommitEdge']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'commit_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['vcsinfo.Repository']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        'vcsinfo.commitedge': {
            'Meta': {'object_name': 'CommitEdge'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Commit_parent'", 'to': "orm['vcsinfo.Commit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Commit_child'", 'to': "orm['vcsinfo.Commit']"})
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

    complete_apps = ['vcsinfo']
