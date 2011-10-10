# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Asset'
        db.create_table('video_asset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('mpaa', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['video.Category'])),
            ('imdbID', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('playURL', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('desc', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('video', ['Asset'])

        # Adding model 'Catalog'
        db.create_table('video_catalog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('icon', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('model', self.gf('django.db.models.fields.CharField')(default=u'LOCAL', max_length=100)),
            ('modelProxy', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('video', ['Catalog'])

        # Adding model 'Category'
        db.create_table('video_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('catalog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['video.Catalog'])),
        ))
        db.send_create_signal('video', ['Category'])

        # Adding model 'Genre'
        db.create_table('video_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['video.Category'])),
        ))
        db.send_create_signal('video', ['Genre'])

        # Adding model 'GenreAssetGroup'
        db.create_table('video_genreassetgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Genre'])),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['video.Asset'])),
        ))
        db.send_create_signal('video', ['GenreAssetGroup'])

        # Adding model 'Transaction'
        db.create_table('video_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tstamp', self.gf('django.db.models.fields.DateField')()),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['video.Asset'])),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscribers.Subscriber'])),
        ))
        db.send_create_signal('video', ['Transaction'])


    def backwards(self, orm):
        
        # Deleting model 'Asset'
        db.delete_table('video_asset')

        # Deleting model 'Catalog'
        db.delete_table('video_catalog')

        # Deleting model 'Category'
        db.delete_table('video_category')

        # Deleting model 'Genre'
        db.delete_table('video_genre')

        # Deleting model 'GenreAssetGroup'
        db.delete_table('video_genreassetgroup')

        # Deleting model 'Transaction'
        db.delete_table('video_transaction')


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
        },
        'video.asset': {
            'Meta': {'object_name': 'Asset'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['video.Category']"}),
            'desc': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdbID': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'mpaa': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'playURL': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'video.catalog': {
            'Meta': {'object_name': 'Catalog'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'default': "u'LOCAL'", 'max_length': '100'}),
            'modelProxy': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'video.category': {
            'Meta': {'object_name': 'Category'},
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['video.Catalog']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'video.genre': {
            'Meta': {'object_name': 'Genre'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['video.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'video.genreassetgroup': {
            'Meta': {'object_name': 'GenreAssetGroup'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['video.Asset']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['channels.Genre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'video.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['video.Asset']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscribers.Subscriber']"}),
            'tstamp': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['video']
