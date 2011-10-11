#
# This is an internal tool to test SYNET-based set top boxes, 
# and therefore no applicability to commercial use is guaranteed
#
# Copyright (c) 2011 SYNESIS LLC
# www.synesis.ru
# 
# SYNESIS hereby provides you with non-exclusive, non-transferrable license 
# to use this software within your organization, solely to to interface with 
# set top boxes running SYNET middleware from SYNESIS
# 
# Any further questions please address to synet@synesis.ru
# Technical suppport is available at http://synet.synesis.ru
#

#
# this module abstracts working with channels, it doesn't go into details of whether it's a DVB, IPTV or OTT channel
#

from django.db import models
from subscribers.models import Subscriber

MPAA_RATING = (
	(u"G", u'[G] General audiences'),
	(u"PG", u'[PG] Parental guidance suggested'),
	(u"PG-13",u'[PG-13] Parents strongly cautioned'),
	(u"R", u'[R] Restricted'),
	(u"NC", u"[NC-17] Noone below 17"),
	(u"XX", u"[XXX] Porn")
)

CHAN_TYPE = (
	(u'TV',		u'TV channel'),
	(u'RADIO',	u'Radio channel')
)

MODULATION_TYPE = (
	(u'QAM256',	u'QAM-256'),
	(u'QAM56',	u'QAM-56')
)

SERVICE_MODE = (
	(u'DVB', 	u"DVB Cable"),
	(u'IPTV', 	u"IPTV Multicast"),
	(u'OTT', 	u'Over-the-internet')
)

# still need to be aware of DVB Muxes
class DvbMux (models.Model):
	fec_hp	= models.CharField(u'FEC_HP', max_length=10, blank=False)
	fec_lp	= models.CharField(u'FEC_LP', max_length=10, blank=False)
	freq	= models.PositiveIntegerField(u"Frequency Hz")
	modulation = models.CharField(u"modulation", choices=MODULATION_TYPE, max_length=10, blank=False)
	symbolRate = models.PositiveIntegerField(u"Symbol rate")
	
	def __unicode__(self):
		return "%s @ %d Khz @ %d Ksym" % (self.modulation, (self.freq)/1000, (self.symbolRate/1000))
	
class Channel (models.Model):
	name 	= models.CharField(u"Name", help_text="channel human visible name", unique=True, max_length=100)
	xmltvID = models.PositiveIntegerField(u"XMLTV ID", unique=True, help_text="channel logical name as seen by STB and refered by EPG server")
	lcn		= models.PositiveIntegerField(u"LCN", help_text="Logical channel number, defines channel order")
	tune  	= models.TextField(u"channel tune parameters", help_text="serialized form of channel tune data")
	enabled	= models.BooleanField(default=True)	
	mpaa 	= models.CharField(u'MPAA raiting', max_length=5, choices=MPAA_RATING)
	mode	= models.CharField(u'Channel mode', max_length=5, choices=SERVICE_MODE, default=u'DVB')
	chanType= models.CharField(u'Channel type', max_length=5, choices=CHAN_TYPE, default=u'TV')
	mux		= models.ForeignKey(DvbMux, blank=True, null=True)
	
	demoURL	= models.URLField(u'Teaser movie URL', verify_exists=True, help_text="HTTP Live streaming (.m3u8) or .mp4 over HTTP to display if channel is unavailable as part of current user's subscription")
	
	def __unicode__(self):
		return "%s [xmltvID=%d]"%(self.name, self.xmltvID)
	
class Tariff (models.Model):
	name 		= models.CharField(u"tariff name", max_length=100)
	channels	= models.ManyToManyField(Channel, through="TariffGroup")
	enabled 	= models.BooleanField()
	cost		= models.CharField(u"cost in local currency", max_length=20, blank=True)
	
	def __unicode__(self):
		if (self.cost != None):
			return "%s [%s]" % (self.name, self.cost)
		else:
			return self.name
	
	# list view oriented helpers 
	def countSubscribers(self):
		return self.subscribers.all().count()
	def countChannels(self):
		return self.channels.all().count()
	countSubscribers.short_description 	= "# Subscribers"
	countChannels.short_description 	= "# Channels"

# private, to bind tariff & channels
#
class TariffGroup (models.Model):
	channel = models.ForeignKey(Channel)
	tariff  = models.ForeignKey(Tariff)
	
	def test(self):
		return channel.name
	
class TariffAssignments (models.Model):
	subscriber = models.ForeignKey(Subscriber)
	tariff	   = models.ForeignKey(Tariff)

# assignment of genres to channel top level categories
class Genre (models.Model):
	name = models.CharField(u"Genre", max_length=40, unique=True)
	def __unicode__(self):
		return self.name

class ChannelCategory (models.Model):
	name = models.CharField(u"Channel category", max_length=40)
	channels = models.ManyToManyField(Channel, verbose_name=u'Channel(s)', through='ChannelCategory_Group')
	genres   = models.ManyToManyField(Genre, verbose_name=u'Channel(s)', through='ChannelCategory_Genre_Group')
	code	 = models.PositiveIntegerField(u'code for external reference')

	def __unicode__(self):
		return self.name
	
	def countChannels(self):
		return self.channels.all().count()
	countChannels.short_description = u"# Channels"
	
	def countGenres(self):
		return self.genres.all().count()
	countGenres.short_description = u"# Genres"

# assigning channel to specific group
class ChannelCategory_Group (models.Model):
	channel = models.ForeignKey(Channel)
	category = models.ForeignKey(ChannelCategory)

	def __unicode__(self):
		return "Category %s assignment to channel %s" % (self.category.name, self.channel.name)

class ChannelCategory_Genre_Group (models.Model):
	channelCategory = models.ForeignKey(ChannelCategory)
	genre = models.ForeignKey(Genre)