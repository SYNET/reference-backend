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
from django.db.models import Min, Max
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

def noEntries():
	return HttpResponse("<error><msg>No Entries</msg></error>")

def recordName(record):
	return record.title
#
# Returns further URIs to available catalog
#
def Catalog(request):
	rX = ET.Element("elements")
	for ch in Channel.objects.filter(npvrEnabled=True):
		ET.SubElement(rX, "list", attrib={'navigateUrl' : request.build_absolute_uri(BASE_URL+"/channel/%d"%ch.xmltvID)}).text=ch.name
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))

# 
# presents main catalog by channel
# 
def ChannelCatalog(request, channelXmltvID):
	dR = NpvrRecord.objects.filter(channel__xmltvID=int(channelXmltvID)).aggregate(Min('airTime'), Max('airTime'))
	if dR['airTime__min'] is None or dR['airTime__max'] is None:
		return noEntries()
	
	# present day by day list
	rX = ET.Element("elements")
	day= datetime.datetime(year = dR['airTime__min'].year,
							month = dR['airTime__min'].month,
							day   = dR['airTime__min'].day) 
	while day < dR['airTime__max']:
		ET.SubElement(rX, "list", 
			attrib={'navigateUrl' : request.build_absolute_uri(BASE_URL+"/channel/%s/%d/%d/%d" % (channelXmltvID, day.year, day.month, day.day))}
			).text = "%d/%d" % (day.month, day.day)
		day += datetime.timedelta(days=1)
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))

def ChannelCatalogByDay(request, channelXmltvID, year, month, day):
	dayFrom = datetime.datetime(int(year), int(month), int(day))
	records = NpvrRecord.objects.filter(channel__xmltvID=int(channelXmltvID),
										airTime__gte=dayFrom,
										airTime__lte=dayFrom+datetime.timedelta(hours=23, minutes=59))
	
	rX = ET.Element("elements")
	for record in records: 
		ET.SubElement(rX, "asset", attrib={'infoUrl' : request.build_absolute_uri(BASE_URL+"/record/%d" % record.id)}).text = recordName(record)
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))

def RecordInfo(request, recordID):
	try : 
		record = NpvrRecord.objects.get(id=int(recordID))
	except NpvrRecord.DoesNotExist as e:
		return HttpResponse("<error>invalid request</error>", status=404)
	
	infoX = ET.Element('info')
	metaX = ET.SubElement(infoX, 'metadata')
	
	if record.posterUrl != None and record.posterUrl != '':
		ET.SubElement(metaX, 'poster', attrib={'smallImageUrl' : record.posterUrl})
	
	# now we provide information about channel and air time
	dataX = ET.SubElement(metaX, 'data')
	dataX.tail = 'Hi there'
	ET.SubElement(ET.SubElement(dataX, 'group'),
	 'item', attrib={
		'label'		: record.title
	})
	ET.SubElement(ET.SubElement(dataX, 'group', attrib={'label' : "Channel "}),
	 'item', attrib={
		'label' 	: record.channel.name,
		'filterUrl'	: request.build_absolute_uri(BASE_URL + '/channel/%d' % record.channel.xmltvID) 
	})
	ET.SubElement(ET.SubElement(dataX, 'group', attrib={'label': 'Air Time '}),
	 'item', attrib={
		'label' : "%d/%d %d:%d" % (record.airTime.month, record.airTime.day, record.airTime.hour, record.airTime.minute)
	})
	
	if record.catalogID != None and record.catalogID != 0:
		count = NpvrRecord.objects.filter(catalogID=record.catalogID).count()
		if count > 0:
			ET.SubElement(ET.SubElement(dataX, 'group', attrib={'label' : 'Other series of %s'%record.title}),
			 'item', attrib={
				'label' 	: u" %d more"%count,
				'filterUrl' : request.build_absolute_uri('/synet/npvr/record/catalog/%d'%record.catalogID)
			})
	
	ET.SubElement(infoX, 'description').text = record.description	
	ET.SubElement(infoX, 'purchase', attrib={'playUrl' : request.build_absolute_uri('/synet/asset/%d/play/hls.m3u8'%record.id)})
	return HttpResponse(ET.tostring(infoX, encoding='utf-8'))

def RecordsByCatalogId(request, catalogID):
	rX = ET.Element("elements")
	
	for record in NpvrRecord.objects.filter(catalogID=catalogID):
		ET.SubElement(rX, 'item', 
		attrib={'filterUrl' : request.build_absolute_uri('/synet/npvr/record/%d'%record.id)}
		).text = recordName(record)
	
	return HttpResponse(ET.tostring(rX, encoding='utf-8'))
