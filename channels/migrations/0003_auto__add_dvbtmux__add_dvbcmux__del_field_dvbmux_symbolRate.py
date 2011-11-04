# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DvbTMux'
        db.create_table('channels_dvbtmux', (
            ('dvbmux_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['channels.DvbMux'], unique=True, primary_key=True)),
            ('bandwidth', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('guardInterval', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('hierarchy', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('transmitMode', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('channels', ['DvbTMux'])

        # Adding model 'DvbCMux'
        db.create_table('channels_dvbcmux', (
            ('dvbmux_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['channels.DvbMux'], unique=True, primary_key=True)),
            ('symbolRate', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('channels', ['DvbCMux'])

        # Deleting field 'DvbMux.symbolRate'
        db.delete_column('channels_dvbmux', 'symbolRate')


    def backwards(self, orm):
        
        # Deleting model 'DvbTMux'
        db.delete_table('channels_dvbtmux')

        # Deleting model 'DvbCMux'
        db.delete_table('channels_dvbcmux')

        # User chose to not deal with backwards NULL issues for 'DvbMux.symbolRate'
        raise RuntimeError("Cannot reverse this migration. 'DvbMux.symbolRate' and its values cannot be restored.")


    models = {
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
        'channels.channelcategory': {
            'Meta': {'object_name': 'ChannelCategory'},
            'channels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['channels.Channel']", 'through': "orm['channels.ChannelCategory_Group']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['channels.Genre']", 'through': "orm['channels.ChannelCategory_Genre_Group']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'channels.channelcategory_genre_group': {
            'Meta': {'object_name': 'ChannelCategory_Genre_Group'},
            'channelCategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.ChannelCategory']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Genre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'channels.channelcategory_group': {
            'Meta': {'object_name': 'ChannelCategory_Group'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.ChannelCategory']"}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Channel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'channels.dvbcmux': {
            'Meta': {'object_name': 'DvbCMux', '_ormbases': ['channels.DvbMux']},
            'dvbmux_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['channels.DvbMux']", 'unique': 'True', 'primary_key': 'True'}),
            'symbolRate': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'channels.dvbmux': {
            'Meta': {'object_name': 'DvbMux'},
            'fec_hp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fec_lp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'freq': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modulation': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'channels.dvbtmux': {
            'Meta': {'object_name': 'DvbTMux', '_ormbases': ['channels.DvbMux']},
            'bandwidth': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'dvbmux_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['channels.DvbMux']", 'unique': 'True', 'primary_key': 'True'}),
            'guardInterval': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'hierarchy': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'transmitMode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'channels.genre': {
            'Meta': {'object_name': 'Genre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'channels.tariff': {
            'Meta': {'object_name': 'Tariff'},
            'channels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['channels.Channel']", 'through': "orm['channels.TariffGroup']", 'symmetrical': 'False'}),
            'cost': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'channels.tariffassignments': {
            'Meta': {'object_name': 'TariffAssignments'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscribers.Subscriber']"}),
            'tariff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Tariff']"})
        },
        'channels.tariffgroup': {
            'Meta': {'object_name': 'TariffGroup'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Channel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tariff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Tariff']"})
        },
        'subscribers.subscriber': {
            'Meta': {'object_name': 'Subscriber'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'agreement': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'tariffs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['channels.Tariff']", 'through': "orm['channels.TariffAssignments']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['channels']
