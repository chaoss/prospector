# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MicroblogProvider'
        db.create_table(u'microbloginfo_microblogprovider', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('username', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('password', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'microbloginfo', ['MicroblogProvider'])

        # Adding model 'Microblog'
        db.create_table(u'microbloginfo_microblog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['microbloginfo.MicroblogProvider'])),
            ('handle', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'microbloginfo', ['Microblog'])

        # Adding M2M table for field projects on 'Microblog'
        m2m_table_name = db.shorten_name(u'microbloginfo_microblog_projects')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('microblog', models.ForeignKey(orm[u'microbloginfo.microblog'], null=False)),
            ('project', models.ForeignKey(orm[u'projectinfo.project'], null=False))
        ))
        db.create_unique(m2m_table_name, ['microblog_id', 'project_id'])

        # Adding model 'MicroblogPost'
        db.create_table(u'microbloginfo_microblogpost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post_id', self.gf('django.db.models.fields.TextField')()),
            ('microblog', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posts', to=orm['microbloginfo.Microblog'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('reposts', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'microbloginfo', ['MicroblogPost'])

        # Adding unique constraint on 'MicroblogPost', fields ['microblog', 'post_id']
        db.create_unique(u'microbloginfo_microblogpost', ['microblog_id', 'post_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'MicroblogPost', fields ['microblog', 'post_id']
        db.delete_unique(u'microbloginfo_microblogpost', ['microblog_id', 'post_id'])

        # Deleting model 'MicroblogProvider'
        db.delete_table(u'microbloginfo_microblogprovider')

        # Deleting model 'Microblog'
        db.delete_table(u'microbloginfo_microblog')

        # Removing M2M table for field projects on 'Microblog'
        db.delete_table(db.shorten_name(u'microbloginfo_microblog_projects'))

        # Deleting model 'MicroblogPost'
        db.delete_table(u'microbloginfo_microblogpost')


    models = {
        u'microbloginfo.microblog': {
            'Meta': {'object_name': 'Microblog'},
            'handle': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'related_name': "'microblogs'", 'blank': 'True', 'to': u"orm['projectinfo.Project']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microbloginfo.MicroblogProvider']"})
        },
        u'microbloginfo.microblogpost': {
            'Meta': {'unique_together': "(('microblog', 'post_id'),)", 'object_name': 'MicroblogPost'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'microblog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': u"orm['microbloginfo.Microblog']"}),
            'post_id': ('django.db.models.fields.TextField', [], {}),
            'reposts': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'microbloginfo.microblogprovider': {
            'Meta': {'object_name': 'MicroblogProvider'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'password': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'username': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
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
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['projectinfo.Project']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['microbloginfo']
