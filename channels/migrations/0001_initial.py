# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DvbMux'
        db.create_table('channels_dvbmux', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fec_hp', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fec_lp', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('freq', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('modulation', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('symbolRate', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('channels', ['DvbMux'])

        # Adding model 'Channel'
        db.create_table('channels_channel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('xmltvID', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('lcn', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('tune', self.gf('django.db.models.fields.TextField')()),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('mpaa', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('mode', self.gf('django.db.models.fields.CharField')(default=u'DVB', max_length=5)),
            ('chanType', self.gf('django.db.models.fields.CharField')(default=u'TV', max_length=5)),
            ('mux', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.DvbMux'], null=True, blank=True)),
            ('demoURL', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('channels', ['Channel'])

        # Adding model 'Tariff'
        db.create_table('channels_tariff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cost', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('channels', ['Tariff'])

        # Adding model 'TariffGroup'
        db.create_table('channels_tariffgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'])),
            ('tariff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Tariff'])),
        ))
        db.send_create_signal('channels', ['TariffGroup'])

        # Adding model 'TariffAssignments'
        db.create_table('channels_tariffassignments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscribers.Subscriber'])),
            ('tariff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Tariff'])),
        ))
        db.send_create_signal('channels', ['TariffAssignments'])

        # Adding model 'Genre'
        db.create_table('channels_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('channels', ['Genre'])

        # Adding model 'ChannelCategory'
        db.create_table('channels_channelcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('code', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('channels', ['ChannelCategory'])

        # Adding model 'ChannelCategory_Group'
        db.create_table('channels_channelcategory_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.ChannelCategory'])),
        ))
        db.send_create_signal('channels', ['ChannelCategory_Group'])

        # Adding model 'ChannelCategory_Genre_Group'
        db.create_table('channels_channelcategory_genre_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channelCategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.ChannelCategory'])),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Genre'])),
        ))
        db.send_create_signal('channels', ['ChannelCategory_Genre_Group'])


    def backwards(self, orm):
        
        # Deleting model 'DvbMux'
        db.delete_table('channels_dvbmux')

        # Deleting model 'Channel'
        db.delete_table('channels_channel')

        # Deleting model 'Tariff'
        db.delete_table('channels_tariff')

        # Deleting model 'TariffGroup'
        db.delete_table('channels_tariffgroup')

        # Deleting model 'TariffAssignments'
        db.delete_table('channels_tariffassignments')

        # Deleting model 'Genre'
        db.delete_table('channels_genre')

        # Deleting model 'ChannelCategory'
        db.delete_table('channels_channelcategory')

        # Deleting model 'ChannelCategory_Group'
        db.delete_table('channels_channelcategory_group')

        # Deleting model 'ChannelCategory_Genre_Group'
        db.delete_table('channels_channelcategory_genre_group')


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
        'channels.dvbmux': {
            'Meta': {'object_name': 'DvbMux'},
            'fec_hp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fec_lp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'freq': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modulation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'symbolRate': ('django.db.models.fields.PositiveIntegerField', [], {})
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
