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

SYM_PARAM_SIZE = 30

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
	(u'QAM64', 	u'QAM-64'),
	(u'QAM256',	u'QAM-256'),
	(u'QAM56',	u'QAM-56')
)

BANDWIDTH_MODE = (
	(u"BANDWIDTH_8", u'8'),
	(u"BANDWIDTH_7", u'7'),
	(u"BANDWIDTH_6", u'6'),
	(u"BANDWIDTH_AUTO", u'Auto')
)

HIERARCHY_MODE = (
	(u"HIERARCHY_NONE", u'None'),
	(u"HIERARCHY_1", u'1'),
	(u"HIERARCHY_2", u'2'),
	(u"HIERARCHY_3", u'3'),
	(u"HIERARCHY_4", u'4'),
	(u"HIERARCHY_AUTO", u'Auto')
)

GUARD_INTERVAL = (
	(u"GUARD_1_32", u'1/32'),
	(u"GUARD_1_16", u'1/16'),
	(u"GUARD_1_8", u'1/8'),
	(u"GUARD_1_4", u'1/4'),
	(u"GUARD_AUTO", u'Auto')
)

TRANSMIT_MODE = (
	(u"TRANSMIT_2K", u'2K'),
	(u"TRANSMIT_8K", u'8K'),
	(u"TRANSMIT_AUTO", u'Auto'),
)

# still need to be aware of DVB Muxes
class DvbMux (models.Model):
	fec_hp	= models.CharField(u'FEC_HP', max_length=SYM_PARAM_SIZE, blank=False)
	fec_lp	= models.CharField(u'FEC_LP', max_length=SYM_PARAM_SIZE, blank=False)
	freq	= models.PositiveIntegerField(u"Frequency Hz")
	modulation = models.CharField(u"modulation", choices=MODULATION_TYPE, max_length=SYM_PARAM_SIZE, blank=False)
	
	def type(self):
		m = 'ERROR'
		try : 
			m = self.dvbcmux
			return 'DVB-C'
		except DvbCMux.DoesNotExist, e:
			pass
		
		try:
			m = self.dvbtmux
			return 'DVB-T'
		except DvbTMux.DoesNotExist, e:
			pass
		
		return m

	def __unicode__(self):
		m = self.type()
		if m == 'DVB-C':
			return "DVB-C %s @ %d Khz, %d KSym" % (self.modulation, (self.freq)/1000, self.dvbcmux.symbolRate/1000)
		elif m == 'DVB-T':
			return "DVB-T %s @ %d Khz, band=%s, transmit=%s" % (self.modulation, self.freq / 1000, self.dvbtmux.bandwidth, self.dvbtmux.transmitMode)
		else:
			return 'Unknown MUX type'

class DvbTMux (DvbMux):
	bandwidth		= models.CharField(u'Bandwidth', max_length=SYM_PARAM_SIZE, choices=BANDWIDTH_MODE, blank=False)
	guardInterval	= models.CharField(u'Guard Interval', max_length=SYM_PARAM_SIZE, choices=GUARD_INTERVAL, blank=False)
	hierarchy		= models.CharField(u'Hierarchy', max_length=SYM_PARAM_SIZE, choices=HIERARCHY_MODE, blank=False)
	transmitMode	= models.CharField(u'Transmit mode', max_length=SYM_PARAM_SIZE, choices=TRANSMIT_MODE, blank=False)

class DvbCMux (DvbMux):
	symbolRate = models.PositiveIntegerField(u"Symbol rate")

# channel information is abstracted from dvb/iptv delivery method
# if channel is bound to DVB-T mux, it would be generated as DVB-T
# if channel has multicast (which is common for IP-based headends) it would be used for NPVR 
# and also you could use this channel data with IPTV STBs
class Channel (models.Model):
	name 	= models.CharField(u"Name", help_text="channel human visible name", unique=True, max_length=100)
	xmltvID = models.PositiveIntegerField(u"XMLTV ID", unique=True, help_text="channel logical name as seen by STB and refered by EPG server")
	lcn		= models.PositiveIntegerField(u"LCN", help_text="Logical channel number, defines channel order")
	tune  	= models.TextField(u"channel tune parameters", help_text="serialized form of channel tune data")
	enabled	= models.BooleanField(u'Show to users', default=True)	
	mpaa 	= models.CharField(u'MPAA raiting', max_length=5, choices=MPAA_RATING)
	chanType= models.CharField(u'Channel type', max_length=5, choices=CHAN_TYPE, default=u'TV')
	mux		= models.ForeignKey(DvbMux, blank=True, null=True)
	
	demoURL	= models.URLField(u'Teaser movie URL', verify_exists=True, blank=True, null=True, default=None, help_text="HTTP Live streaming (.m3u8) or .mp4 over HTTP to display if channel is unavailable as part of current user's subscription")
	
	# for NPVR - defines a source of multicast address to obtain raw SPTS signal
	mcastAddr 	= models.IPAddressField(u"Multicast address", blank=True, null=True, default=None)
	mcastPort	= models.PositiveIntegerField(u'Multicast Port', blank=True, null=True, default=None)
	npvrEnabled	= models.BooleanField(u'Enable NPVR', default=False)
	
	def __unicode__(self):
		return "%s [xmltvID=%d]"%(self.name, self.xmltvID)
	
	class Meta:
		unique_together = (u'mcastAddr', u'mcastPort')
	
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
	
	class Meta:
		unique_together = ('channel', 'tariff')

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
	code	 = models.PositiveIntegerField(u'code for external reference', unique=True)

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
