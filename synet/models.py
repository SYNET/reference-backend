# coding=utf-8

from django.db import models
from channels.models import Channel 
from subscribers.models import Subscriber

IGMP_CHOICES = (
	(2, u'IGMP Version 2'),
	(3, u'IGMP Version 3')
)

TIMEZONE_CHOICES = (
	(u'gmt',				u'GMT +0'),
	(u'europe/warsaw',		u'Warsaw'),
	(u'europe/moscow',		u'Москва'),
	(u'europe/vilnius',		u'Vilnius'),
	(u'asia/yekaterinburg', u'Екатеринбург'),
	(u'asia/omsk',			u'Омск'),
	(u'asia/krasnoyarsk',	u'Красноярск'),
	(u'asia/irkutsk',		u'Иркутск'),
	(u'asia/yakutsk',		u'Якутск'),
	(u'asia/vladivostok',	u'Владивосток'),
	(u'asia/magadan',		u'Магадан'),
	(u'europe/minsk',		u'Минск'),
	(u'europe/tallinn',		u'Tallinn'),
	(u'europe/riga',		u'Riga'),
	(u'europe/sofia',		u'Sofia'),
	(u'europe/amsterdam',	u'Amsterdam'),
	(u'europe/budapest',	u'Budapest'),
	(u'europe/ljubljana',	u'Ljubljana'),
	(u'europe/london',		u'UK - London'),
	(u'europe/kaliningrad', u'Калиниград'),
)

SYNET_HMI_LOCALES = (
	(u'eng',	u'English'),
	(u'rus',	u'Russian'),
	(u'pol',    u'Polish'),
	(u'est',    u'Estonian'),
	(u'lav',    u'Latvian'),
	(u'lit',    u'Lithuanian'),
	(u'bul',    u'Bulgarian'),
	(u'dut',    u'Dutch'),
	(u'hun',    u'Hungarian'),
	(u'slv',    u'Slovenian'),
)

SERVICE_MODE = (
	(u'DVB', 	u"DVB Cable"),
	(u'IPTV', 	u"IPTV Multicast"),
	(u'OTT', 	u'Over-the-internet')
)

#
# firmware holds information about available versions
# 
class Firmware(models.Model):
	version			= models.CharField('Version', max_length=20, blank=False)
	url				= models.URLField('URL', verify_exists=True, unique=True)
	message			= models.TextField('Message to display while upgrading')
	
	def countUsage(self):
		from synet.models import STB
		return u'%d STBs run it' % STB.objects.filter(fwVersion=self.version).count()
	
	def __unicode__(self):
		return self.version

#
# Service is a holder to multiple configuration settings
#
class Service(models.Model):
	enabled			= models.BooleanField('Active service', default=False)
	serviceType		= models.CharField(max_length=10, choices=SERVICE_MODE, blank=False, default=u'DVB')
	name			= models.CharField(max_length=20, unique=True)
	igmpVersion		= models.PositiveIntegerField('IGMP version', blank=True, choices=IGMP_CHOICES, default=2,
		help_text='Valid for IPTV multicast only, see <a href=\"http://synet.synesis.ru/entries/20022298-igmp\" target=_blank>IGMP Version select</a>')
	ntpAddr			= models.IPAddressField('NTP server', help_text="Network time protocol server")
	currentFW		= models.ForeignKey(Firmware, verbose_name="Firmware", blank=True, null=True)
	forceFWUpdate	= models.BooleanField('Force firmware update', default=False)
	hmiLocale		= models.CharField('GUI language', max_length=5, choices=SYNET_HMI_LOCALES)
	timeZone		= models.CharField('Timezone', max_length=20, choices=TIMEZONE_CHOICES, blank=False)
	autoTuneChan	= models.ForeignKey(Channel, blank=True, null=True,
		help_text='<a href=\"http://synet.synesis.ru/entries/20198996\" target=_blank >Auto tuning</a>')
	epgServerUrl	= models.URLField('URL to EPG server', verify_exists=False,
		help_text='see <a href=\"http://synet.synesis.ru/forums/20028386-epg\" target=\"_blank\">EPG Server Configuration</a>')
	statServerUrl	= models.URLField('URL to statistics server', verify_exists=False)
	# service can redirect connections to other servers
	# this allows to have i.e. 'production' and 'staging' servers
	redirect		= models.BooleanField("Redirect", default=False)
	redirectURL		= models.URLField('Configuration redirect URL', verify_exists=False, blank=True)
	# tariff management could be either None, Local or external
	
	def __unicode__(self):
		return self.name
	
	# we may assign specific STBs to be used by this service,
	# this is done by having a foreign key to Service in STB class 
	# if blank, all STBs are served by this Service instance
	# TODO: bind fwVersion - it's supposed to be up-to-date	and bound to Firmware

class STB(models.Model):
	subscriber	= models.ForeignKey(Subscriber, blank=True, null=True)
	macAddr		= models.CharField(max_length=17,  blank=False, unique=True)
	hashKey		= models.CharField(max_length=512, blank=False, unique=True)
	fwVersion	= models.CharField(max_length=200, blank=False, )
	service		= models.ForeignKey(Service, blank=True, null=True, default=None)

