# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Asset'
        db.create_table('asset_asset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('appType', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('asset', ['Asset'])

        # Adding model 'Chunk'
        db.create_table('asset_chunk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sequenceNumber', self.gf('django.db.models.fields.IntegerField')()),
            ('appType', self.gf('django.db.models.fields.IntegerField')()),
            ('inAppId', self.gf('django.db.models.fields.IntegerField')(max_length=20)),
            ('durationMs', self.gf('django.db.models.fields.IntegerField')()),
            ('startTime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Asset'], null=True, blank=True)),
            ('dataUrl', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('aesKey', self.gf('django.db.models.fields.CharField')(max_length=48)),
            ('aesIV', self.gf('django.db.models.fields.CharField')(max_length=48)),
        ))
        db.send_create_signal('asset', ['Chunk'])

        # Adding unique constraint on 'Chunk', fields ['sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl']
        db.create_unique('asset_chunk', ['sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl'])

        # Adding model 'Entitlement'
        db.create_table('asset_entitlement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('effectiveFrom', self.gf('django.db.models.fields.DateTimeField')()),
            ('effectiveTo', self.gf('django.db.models.fields.DateTimeField')()),
            ('clientIP', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Asset'])),
        ))
        db.send_create_signal('asset', ['Entitlement'])

        # Adding model 'ApiKeys'
        db.create_table('asset_apikeys', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('asset', ['ApiKeys'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Chunk', fields ['sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl']
        db.delete_unique('asset_chunk', ['sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl'])

        # Deleting model 'Asset'
        db.delete_table('asset_asset')

        # Deleting model 'Chunk'
        db.delete_table('asset_chunk')

        # Deleting model 'Entitlement'
        db.delete_table('asset_entitlement')

        # Deleting model 'ApiKeys'
        db.delete_table('asset_apikeys')


    models = {
        'asset.apikeys': {
            'Meta': {'object_name': 'ApiKeys'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'asset.asset': {
            'Meta': {'object_name': 'Asset'},
            'appType': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'asset.chunk': {
            'Meta': {'unique_together': "(('sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl'),)", 'object_name': 'Chunk'},
            'aesIV': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'aesKey': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'appType': ('django.db.models.fields.IntegerField', [], {}),
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['asset.Asset']", 'null': 'True', 'blank': 'True'}),
            'dataUrl': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'durationMs': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inAppId': ('django.db.models.fields.IntegerField', [], {'max_length': '20'}),
            'sequenceNumber': ('django.db.models.fields.IntegerField', [], {}),
            'startTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'asset.entitlement': {
            'Meta': {'object_name': 'Entitlement'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['asset.Asset']"}),
            'clientIP': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'effectiveFrom': ('django.db.models.fields.DateTimeField', [], {}),
            'effectiveTo': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['asset']
