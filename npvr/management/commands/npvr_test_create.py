#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2011 Synesis LLC.
#
# Technical support and updates: http://synet.synesis.ru
# You are free to use this software for evaluation and commercial purposes
# under condition that it is used only in conjunction with digital TV
# receivers running SYNET middleware by Synesis.
# 
# To contribute modifcations, additional modules and derived works please
# contact pnx@synesis.ru

from epg import xmltv
from dateutil import parser
from datetime import datetime
import sys
import time, calendar
import codecs
from xml.etree.cElementTree import ElementTree, Element, SubElement, tostring
from django.db import connections, transaction
from django.db.models import Min, Max
from django.core.management.base import BaseCommand, CommandError
from epg.models import EpgCategory, EpgProgram
from asset.models import Chunk, APP_TYPE_NPVR
from channels.models import Channel

#
# This command walks around the channel database,
# and looks for NPVR chunks for channels with NPVR activated
# then constructs the database of NPVR records based on registered chunks from assets package
#
# it is supposed to be invoked periodically via external scheduler, i.e. every 30 minutes
#
class Command(BaseCommand):	
	
	@transaction.commit_on_success
	def handle(self, *args, **options):
		self.stdout = codecs.getwriter('utf-8')(self.stdout, errors='replace')
		self.stderr = codecs.getwriter('utf-8')(self.stderr, errors='replace')
		
		if len(args) == 1:
			try: 
				channels = [Channel.objects.get(xmltvID=int(args[0]))]
			except Channel.DoesNotExist as e:
				raise CommandError("Channel with xmltvID=%d not found\n"%args[0])
		elif len(args) == 0:
			channels = Channel.objects.filter(npvrEnabled=True, enabled=True)
		else:
			raise CommandError(args)
				
		# this test walks over every NPVR-enabled channel NPVR-enabled and then runs 'npvrcreate'
		# there shouldn't be any orphaned chunks left
		for chan in channels:
			sequenceId = 1
			maxmin = EpgProgram.objects.filter(aux_id=u'%d'%chan.xmltvID).aggregate(Min('start'), Max('end'))
			if maxmin['start__min'] is None or maxmin['end__max'] is None: 
				continue
			curTime = maxmin['start__min']
			while curTime < maxmin['end__max']:
				c = Chunk(sequenceNumber = sequenceId, 
					appType 	= APP_TYPE_NPVR,
					inAppId		= chan.xmltvID,
					durationMs	= 10000,
					startTime	= datetime.utcfromtimestamp(curTime))
				c.save()
				sequenceId += 1
				curTime += 10
			self.stdout.write(u'Added %d chunks to channel %d\n' % (sequenceId-1, chan.xmltvID))