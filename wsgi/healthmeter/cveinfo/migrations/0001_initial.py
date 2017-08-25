# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Product'
        db.create_table('cveinfo_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vendor', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('product', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('cveinfo', ['Product'])

        # Adding unique constraint on 'Product', fields ['vendor', 'product']
        db.create_unique('cveinfo_product', ['vendor', 'product'])

        # Adding model 'CVE'
        db.create_table('cveinfo_cve', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('published_datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('cveinfo', ['CVE'])

        # Adding unique constraint on 'CVE', fields ['year', 'number']
        db.create_unique('cveinfo_cve', ['year', 'number'])

        # Adding M2M table for field products on 'CVE'
        db.create_table('cveinfo_cve_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cve', models.ForeignKey(orm['cveinfo.cve'], null=False)),
            ('product', models.ForeignKey(orm['cveinfo.product'], null=False))
        ))
        db.create_unique('cveinfo_cve_products', ['cve_id', 'product_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CVE', fields ['year', 'number']
        db.delete_unique('cveinfo_cve', ['year', 'number'])

        # Removing unique constraint on 'Product', fields ['vendor', 'product']
        db.delete_unique('cveinfo_product', ['vendor', 'product'])

        # Deleting model 'Product'
        db.delete_table('cveinfo_product')

        # Deleting model 'CVE'
        db.delete_table('cveinfo_cve')

        # Removing M2M table for field products on 'CVE'
        db.delete_table('cveinfo_cve_products')


    models = {
        'cveinfo.cve': {
            'Meta': {'unique_together': "(('year', 'number'),)", 'object_name': 'CVE'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'cves'", 'symmetrical': 'False', 'to': "orm['cveinfo.Product']"}),
            'published_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'cveinfo.product': {
            'Meta': {'unique_together': "(('vendor', 'product'),)", 'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cveinfo']
