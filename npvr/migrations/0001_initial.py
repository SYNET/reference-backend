# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NpvrRecord'
        db.create_table('npvr_npvrrecord', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['asset.Asset'], unique=True, primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'])),
            ('airTime', self.gf('django.db.models.fields.DateTimeField')()),
            ('durationSec', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('catalogID', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
            ('posterUrl', self.gf('django.db.models.fields.URLField')(default=None, max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('npvr', ['NpvrRecord'])

        # Adding model 'NpvrRecordsStatistics'
        db.create_table('npvr_npvrrecordsstatistics', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'])),
            ('lastTime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('npvr', ['NpvrRecordsStatistics'])


    def backwards(self, orm):
        
        # Deleting model 'NpvrRecord'
        db.delete_table('npvr_npvrrecord')

        # Deleting model 'NpvrRecordsStatistics'
        db.delete_table('npvr_npvrrecordsstatistics')


    models = {
        'asset.asset': {
            'Meta': {'object_name': 'Asset'},
            'dataBytes': ('django.db.models.fields.BigIntegerField', [], {}),
            'durationMs': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markToDelete': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'channels.channel': {
            'Meta': {'unique_together': "((u'mcastAddr', u'mcastPort'),)", 'object_name': 'Channel'},
            'chanType': ('django.db.models.fields.CharField', [], {'default': "u'TV'", 'max_length': '5'}),
            'demoURL': ('django.db.models.fields.URLField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lcn': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mcastAddr': ('django.db.models.fields.IPAddressField', [], {'default': 'None', 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'mcastPort': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'default': "u'DVB'", 'max_length': '5'}),
            'mpaa': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'mux': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.DvbMux']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'npvrEnabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tune': ('django.db.models.fields.TextField', [], {}),
            'xmltvID': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'})
        },
        'channels.dvbmux': {
            'Meta': {'object_name': 'DvbMux'},
            'fec_hp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fec_lp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'freq': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modulation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'symbolRate': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'npvr.npvrrecord': {
            'Meta': {'object_name': 'NpvrRecord', '_ormbases': ['asset.Asset']},
            'airTime': ('django.db.models.fields.DateTimeField', [], {}),
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['asset.Asset']", 'unique': 'True', 'primary_key': 'True'}),
            'catalogID': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Channel']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'durationSec': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'posterUrl': ('django.db.models.fields.URLField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'npvr.npvrrecordsstatistics': {
            'Meta': {'object_name': 'NpvrRecordsStatistics'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Channel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastTime': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['npvr']
