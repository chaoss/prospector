# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."

        email_addresses = orm['participantinfo.EmailAddress'] \
            .objects \
            .filter(owner__commits__isnull=False) \
            .distinct('owner') \
            .select_related('domainpart', 'owner') \
            .prefetch_related('owner__commits')

        for emailaddr in email_addresses:
            if emailaddr.domainpart is not None:
                email_str = u"{0}@{1}".format(emailaddr.localpart,
                                             emailaddr.domainpart.domain)
            else:
                email_str = unicode(emailaddr.localpart)

            userid = u"{0} <{1}>".format(emailaddr.owner.name, email_str)

            for commit in emailaddr.owner.commits.iterator():
                commit.author_new = orm['vcsinfo.Committer'] \
                    .objects.get_or_create(
                        userid=userid,
                        repository_id=commit.repository_id,
                        defaults={'participant_id': commit.author_id})[0]

                commit.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        # Essentially the same as the following, but in raw SQL since Django
        # can't handle joins in UPDATE statements.
        #
        # orm['vcsinfo.Commit'].objects.update(
        #     author=F('author_new__participant'))
        db.execute("""
        UPDATE vcsinfo_commit c1 SET author_id = (
            SELECT participant_id
            FROM vcsinfo_committer c2
                INNER JOIN vcsinfo_commit c3
                ON c2.id = c3.author_new_id
            WHERE c1.id = c3.id
        )
        """)

    models = {
        'participantinfo.emailaddress': {
            'Meta': {'unique_together': "(('owner', 'localpart', 'domainpart'),)", 'object_name': 'EmailAddress'},
            'domainpart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'null': 'True', 'to': "orm['participantinfo.EmailDomain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localpart': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_addresses'", 'to': "orm['participantinfo.Participant']"})
        },
        'participantinfo.emaildomain': {
            'Meta': {'object_name': 'EmailDomain'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
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
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'null': 'True', 'to': "orm['participantinfo.Participant']"}),
            'author_new': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'null': 'True', 'to': "orm['vcsinfo.Committer']"}),
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
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'repositories'", 'to': "orm['vcsinfo.Type']"}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10000'})
        },
        'vcsinfo.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['participantinfo', 'vcsinfo']
    symmetrical = True
