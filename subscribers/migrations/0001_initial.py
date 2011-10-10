# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Subscriber'
        db.create_table('subscribers_subscriber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agreement', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('subscribers', ['Subscriber'])

        # Adding model 'AccessCard'
        db.create_table('subscribers_accesscard', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscribers.Subscriber'])),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('subscribers', ['AccessCard'])

        # Adding model 'Message'
        db.create_table('subscribers_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscribers.Subscriber'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('urgent', self.gf('django.db.models.fields.BooleanField')(default=False, max_length=10)),
            ('sendDate', self.gf('django.db.models.fields.DateField')()),
            ('readDate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('subscribers', ['Message'])


    def backwards(self, orm):
        
        # Deleting model 'Subscriber'
        db.delete_table('subscribers_subscriber')

        # Deleting model 'AccessCard'
        db.delete_table('subscribers_accesscard')

        # Deleting model 'Message'
        db.delete_table('subscribers_message')


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
        'subscribers.accesscard': {
            'Meta': {'object_name': 'AccessCard'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscribers.Subscriber']"})
        },
        'subscribers.message': {
            'Meta': {'object_name': 'Message'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'readDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sendDate': ('django.db.models.fields.DateField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscribers.Subscriber']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'urgent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'max_length': '10'})
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

    complete_apps = ['subscribers']
