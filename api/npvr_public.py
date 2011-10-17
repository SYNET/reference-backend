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
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.cache import cache_page
from xml.etree import ElementTree as ET
import re, logging, datetime
from channels.models import Channel, DvbMux, ChannelCategory
from synet.models import Service, STB
from api.contract import getSubscriber, SubscriberNotAuthenticated
from npvr.models import NpvrRecord

logger = logging.getLogger(__name__)

BASE_URL = '/synet/npvr'

#
# Provides API between NPVR and STB
#

#
# Returns further URIs to available catalog
#
def Catalog(request):
	rX = ET.Element("elements")
	for id in Channel.objects.filter(npvrEnabled=True).values_list('xmltvID'):
		ET.SubElement(rX, "list", attrib={'navigateUrl' : BASE_URL+"/channel/%d"%id})
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))

# 
# presents main catalog by channel
# 
def ChannelCatalog(request, channelXmltvID):
	dR = NpvrRecord.objects.filter(channel__xmltvID=int(channelXmltvId)).aggregate(Min('startTime'), Max('startTime'))
	if dR['startTime__min'] is None or minmax['startTime__max'] is None:
		return noEntries()
	
	# present day by day list
	rX = ET.Element("elements")
	for i in range((dR['startTime__max']+datetime.timedelta(days=1)-dR['startTime__min']).days):
		day = dR['startTime__max']+datetime.timedelta(days=i)
		ET.SubElement("list", 
			attrib={'navigateUrl' : BASE_URL+"/channel/%s/%d/%d/%d" % (channelXmltvID, day.year, day.month, day.day)}
			).text = "%d/%d" % (day.month, day.day)
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))

def ChannelCatalogByDay(request, channelXmltvID, year, month, day):
	dayFrom = datetime.day(int(year), int(month), int(day))
	records = NpvrRecord.objects.filter(channel__xmltvID=int(channelXmltvId),
										startTime__gte=dayFrom,
										startTime__lt=dayFrom+datetime.timedelate(hours=23, minutes=59))
	
	rX = ET.Element("elements")
	for record in records: 
		ET.SubElement(rX, "item", attrib={'infoUrl' : BASE_URL+"/item/%d" % record.id}).text = record.title
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))

def RecordInfo(request, recordID):
	try : 
		record = NpvrRecord.objects.get(id=int(recordID))
	except NpvrRecord.DoesNotExist as e:
		return HttpResponse("<error>invalid request</error>", code=404)
	
	infoX = ET.Element('info')
	metaX = ET.SubElement(rX, 'metadata')
	
	if record.posterUrl != None and record.posterUrl != '':
		ET.SubElement(metaX, 'poster', attrib={'url' : record.posterUrl})
	
	# now we provide information about channel and air time
	groupX = ET.SubElement(ET.SubElement(metaX, 'data'), 'group')
	ET.SubElement(groupX, 'item', attrib={
		'label' 	: "Channel",
		'filterUrl'	: BASE_URL + '/channel/%d' % record.channel.xmltvID 
	})
	ET.SubElement(groupX, 'item', attrib={
		'Air Time' : "%d/%d %d:%d" % (record.airTime.month, record.airTime.day, record.airTime.hour, record.airTime.minute)
	})
	
	ET.SubElement(infoX, 'description').text = record.description
	
	return HttpResponse(ET.tostring(infoX, encoding='utf-8'))
