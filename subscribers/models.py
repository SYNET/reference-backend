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

from django.db import models
from time import asctime

#from channels.models import Tariff

class Subscriber(models.Model):
	agreement 	= models.CharField(max_length=200, blank=True)
	name		= models.CharField(max_length=200, unique=True)
	address		= models.CharField(max_length=200, blank=True)
	email		= models.EmailField(max_length=75, help_text="Customer's email")
	tariffs		= models.ManyToManyField('channels.Tariff', through='channels.TariffAssignments')
	
	def __unicode__(self):
		return "%s (%s)" % (self.name, self.receivesService())
	
	def receivesService(self):
		enabledAccess = AccessCard.objects.filter(subscriber=self, enabled=True).count()
		if enabledAccess > 0:
			return "%d active access card" % enabledAccess
		else:
			return "No active access cards"

	receivesService.short_description = "Receives service?"

#
# this class represents either a DVB access card (for DVB-C receivers) or login for IPTV
#
class AccessCard (models.Model):
	subscriber	= models.ForeignKey(Subscriber)
	code		= models.CharField(max_length=20, blank=False, editable=True, unique=True)
	pin			= models.CharField("Self-service PIN code", max_length=200, blank=True)
	enabled		= models.BooleanField(default=True)

# messages distributed to clients
# messaging API manages read statuses and you can cleanup updated messages
class Message(models.Model):
	subscriber	= models.ForeignKey(Subscriber)
	subject		= models.CharField(max_length=200)
	text		= models.CharField(max_length=500)
	imageUrl	= models.URLField(u'Image URL', verify_exists=True, blank=True, null=True)
	urgent		= models.BooleanField(max_length=10)
	sendDate	= models.DateField()
	readDate	= models.DateField(blank=True, null=True, editable=False)

	def isRead(self):
		if self.readDate == None:
			return "Unread"
		else:
			return "Read on %s" % asctime(self.sendDate.timetuple())
	isRead.short_description = "Read status"

