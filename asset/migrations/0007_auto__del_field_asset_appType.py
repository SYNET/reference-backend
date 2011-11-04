# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Asset.appType'
        db.delete_column('asset_asset', 'appType')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Asset.appType'
        raise RuntimeError("Cannot reverse this migration. 'Asset.appType' and its values cannot be restored.")


    models = {
        'asset.apikeys': {
            'Meta': {'object_name': 'ApiKeys'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'asset.asset': {
            'Meta': {'object_name': 'Asset'},
            'dataBytes': ('django.db.models.fields.BigIntegerField', [], {}),
            'durationMs': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markToDelete': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'asset.chunk': {
            'Meta': {'unique_together': "(('sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl'),)", 'object_name': 'Chunk'},
            'aesIV': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'aesKey': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'appType': ('django.db.models.fields.IntegerField', [], {}),
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['asset.Asset']", 'null': 'True', 'blank': 'True'}),
            'dataBytes': ('django.db.models.fields.PositiveIntegerField', [], {}),
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
