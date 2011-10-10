# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Firmware'
        db.create_table('synet_firmware', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('synet', ['Firmware'])

        # Adding model 'Service'
        db.create_table('synet_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('serviceType', self.gf('django.db.models.fields.CharField')(default=u'DVB', max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('igmpVersion', self.gf('django.db.models.fields.PositiveIntegerField')(default=2, blank=True)),
            ('ntpAddr', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('currentFW', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['synet.Firmware'], null=True, blank=True)),
            ('forceFWUpdate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hmiLocale', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('timeZone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('autoTuneChan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'], null=True, blank=True)),
            ('epgServerUrl', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('statServerUrl', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('redirect', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('redirectURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('synet', ['Service'])

        # Adding model 'STB'
        db.create_table('synet_stb', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscribers.Subscriber'], null=True, blank=True)),
            ('macAddr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=17)),
            ('hashKey', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('fwVersion', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['synet.Service'], null=True, blank=True)),
        ))
        db.send_create_signal('synet', ['STB'])


    def backwards(self, orm):
        
        # Deleting model 'Firmware'
        db.delete_table('synet_firmware')

        # Deleting model 'Service'
        db.delete_table('synet_service')

        # Deleting model 'STB'
        db.delete_table('synet_stb')


    models = {
        'channels.channel': {
            'Meta': {'object_name': 'Channel'},
            'chanType': ('django.db.models.fields.CharField', [], {'default': "u'TV'", 'max_length': '5'}),
            'demoURL': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lcn': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mode': ('django.db.models.fields.CharField', [], {'default': "u'DVB'", 'max_length': '5'}),
            'mpaa': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'mux': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.DvbMux']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
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
        },
        'synet.firmware': {
            'Meta': {'object_name': 'Firmware'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'synet.service': {
            'Meta': {'object_name': 'Service'},
            'autoTuneChan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Channel']", 'null': 'True', 'blank': 'True'}),
            'currentFW': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['synet.Firmware']", 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'epgServerUrl': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'forceFWUpdate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hmiLocale': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'igmpVersion': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'ntpAddr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'redirect': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redirectURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'serviceType': ('django.db.models.fields.CharField', [], {'default': "u'DVB'", 'max_length': '10'}),
            'statServerUrl': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'timeZone': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'synet.stb': {
            'Meta': {'object_name': 'STB'},
            'fwVersion': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'hashKey': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'macAddr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '17'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['synet.Service']", 'null': 'True', 'blank': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscribers.Subscriber']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['synet']
