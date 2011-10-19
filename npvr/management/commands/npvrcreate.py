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
from asset.models import Asset, Chunk, APP_TYPE_NPVR
from channels.models import Channel
from npvr.models import NpvrRecord, NpvrRecordsStatistics

#
# This command walks around the channel database,
# and looks for NPVR chunks for channels with NPVR activated
# then constructs the database of NPVR records based on registered chunks from assets package
#
# it is supposed to be invoked periodically via external scheduler, i.e. every 30 minutes
#
class Command(BaseCommand):
	args = 'npvrcreate [channel xmltvID]'
	
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
		
		for chan in channels:
			try:
				progress = NpvrRecordsStatistics.objects.get(channel=chan)
			except NpvrRecordsStatistics.DoesNotExist as e:
				# NPVR catalog was never ran against that channel
				progress = NpvrRecordsStatistics(lastTime=datetime.utcfromtimestamp(0), channel=chan)
			
			minmax 	= Chunk.objects.filter(appType=APP_TYPE_NPVR, inAppId=chan.xmltvID, startTime__gte=progress.lastTime).aggregate(Min('startTime'), Max('startTime'))
			if minmax['startTime__min'] is None or minmax['startTime__max'] is None:
				self.stderr.write("*** No new chunks for channel xmltvID=%d. Total %d chunks \n" % (chan.xmltvID, 
									Chunk.objects.filter(appType=APP_TYPE_NPVR, inAppId=chan.xmltvID).count()))
				progress.save()
				continue
			
			# we only handle complete programs. until program is fully complete it won't appear in NPVR
			for prog in EpgProgram.objects.filter(aux_id = u"%s"%chan.xmltvID, 
												start__gte=int(calendar.timegm(minmax['startTime__min'].utctimetuple())), 
												end__lte=int(calendar.timegm(minmax['startTime__max'].utctimetuple()))).order_by('start'):
				chunks = Chunk.objects.filter(appType=APP_TYPE_NPVR, inAppId=chan.xmltvID, 
					startTime__gte=datetime.utcfromtimestamp(prog.start), startTime__lte=datetime.utcfromtimestamp(prog.end)).order_by('startTime')
				asset = Asset(appType=APP_TYPE_NPVR); asset.save();
				record = NpvrRecord(
					asset 	= asset,
					channel	= chan,
					airTime	= datetime.utcfromtimestamp(prog.start),
					durationSec = (prog.end-prog.start), 
					title 	= prog.title,
					description = prog.descr,
					posterUrl	= prog.icon)
				if prog.cat_id != None and prog.cat_id != 0:
					record.catalogID = prog.cat_id;
				else:
					record.catalogID = None
				record.save()
				
				chunks.update(asset = record.asset)
				progress.lastTime = datetime.utcfromtimestamp(prog.end) # update statistics of last processed program. we don't expect any intersections
				self.stdout.write('+ [%d]@%s : %s\n' % (chan.xmltvID, record.airTime, record.title))
			progress.save()
