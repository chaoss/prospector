# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Repository.last_updated'
        db.add_column('vcsinfo_repository', 'last_updated',
                      self.gf('django.db.models.fields.DateTimeField')(default=None, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Repository.last_updated'
        db.delete_column('vcsinfo_repository', 'last_updated')


    models = {
        'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'vcsinfo.branch': {
            'Meta': {'object_name': 'Branch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_commit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'branches'", 'to': "orm['vcsinfo.Commit']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'vcsinfo.commit': {
            'Meta': {'unique_together': "(('repository', 'commit_id'),)", 'object_name': 'Commit'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['vcsinfo.Committer']"}),
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
        'vcsinfo.committer': {
            'Meta': {'unique_together': "(('userid', 'repository'),)", 'object_name': 'Committer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'committer_ids'", 'to': "orm['participantinfo.Participant']"}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'committers'", 'to': "orm['vcsinfo.Repository']"}),
            'userid': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'vcsinfo.repository': {
            'Meta': {'object_name': 'Repository'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
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
