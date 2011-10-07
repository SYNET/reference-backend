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
# This utility imports legacy category association file
# 
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from channels.models import *
from xml.etree import ElementTree as ET

class Command(BaseCommand):
    args = 'file'
    help = 'Imports category definition file into the system and performs genres and channel assignments'

    def handle(self, *args, **options):
		doc = ET.parse(args[0])
		
		# second level categories (genres)
		genres	= {}
		for g in doc.getroot().findall("Category/Category"):
			if Genre.objects.filter(name=g.attrib['name']).count() > 0:
				genres[g.attrib['name']] = Genre.objects.get(name=g.attrib['name'])
			else:
				genres[g.attrib['name']] = Genre(name = g.attrib['name'])
				genres[g.attrib['name']].save()
		
		# first get all top-level categories and push to database
		categories	= {}
		for c in doc.getroot().findall("Category"):
			if c.attrib['channel'] != u'true':
				self.stderr.write('*** non-channel category skipped: %s'%c)
				continue
			
			if ChannelCategory.objects.filter(name=c.attrib['name']).count() > 0:
				cat = ChannelCategory.objects.get(name=c.attrib['name'])
				# removing any old relationships
				cat.genres.all().delete()				
			else:
				cat = ChannelCategory(name = c.attrib['name'],
									  code = int(c.attrib['id']))
			cat.save()
			categories[c.attrib['id']] = cat
			
			# iterate over genres within this category
			for g in c.findall('Category'):
				model = ChannelCategory_Genre_Group(channelCategory=cat, genre=genres[g.attrib['name']])
				model.save()
			
			# iterate over channels
			for chML in c.findall('Channel'):
				try:
					chan = Channel.objects.get(xmltvID = int(chML.attrib['id']))
				except ObjectDoesNotExist:
					self.stderr.write(u'*** Reference to non-existing channel XMLTVID=%s\n' % chML.attrib['id'])
					continue
				ChannelCategory_Group(channel=chan, category=cat).save()
			