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
import re
import logging
from channels.models import Channel, DvbMux, ChannelCategory
from synet.models import Service, STB
from api.contract import getSubscriber, SubscriberNotAuthenticated

logger = logging.getLogger(__name__)

#
# Generates Hybrid DVB channel descriptor
#
#

def DVB_ChannelList(request):
	doc = ET.Element('Multiplexers')
	for mux in DvbMux.objects.all():
		muxML = ET.Element('Multiplexer')
		muxML.attrib['fec_hp'] 		= mux.fec_hp
		muxML.attrib['fec_lp'] 		= mux.fec_lp
		muxML.attrib['freq'] 		= "%d" % mux.freq
		muxML.attrib['modulation']	= mux.modulation
		muxML.attrib['symbol_rate']	= "%d"%mux.symbolRate
		doc.append(muxML)
		
		for ch in mux.channel_set.filter(enabled=True, mode='DVB'):
			srvML	= ET.XML(ch.tune); muxML.append(srvML)
			lcnML 	= ET.Element("LCN"); lcnML.attrib['value'] = "%d"%ch.lcn; srvML.append(lcnML)
			xmltvML = ET.Element("XMLTV"); xmltvML.attrib['id'] = "%d"%ch.xmltvID; srvML.append(xmltvML)
			nameML  = ET.Element("Name"); nameML.attrib['value'] = ch.name; srvML.append(nameML)
			rateML	= ET.Element("Rating"); rateML.attrib['value'] = ch.mpaa; srvML.append(rateML)
			ET.SubElement(srvML, 'Teaser', attrib={'url': "http://192.168.3.45/static/hls2/hls3/philips/variant_philips_1Mbps.m3u8"})
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

# 
# Generates IPTV channel descriptor, defined by:
# 
# per-user channel list is currently not supported,
# as it'll create orphan EPG entries, so we just generate full channel list
#
# this request does not perform any authentication
#
def IPTV_ChannelList(request):
	chanList = Channel.objects.filter(enabled=True, mode='IPTV')
	chanList.order_by('lcn')
	
	root = ET.Element("ServiceDiscovery")
	e_bd = ET.Element("BroadcastDiscovery")
	root.append(e_bd)
	serviceList = ET.Element("ServiceList")
	e_bd.append(serviceList)
	
	for chan in chanList: 
		# try to parse the string, which must be in 
		# udp://address:port format
		
		serviceParam = re.match(u"udp://(?P<host>[a-zA-Z0-9_\.]+):(?P<port>\w+)", chan.tune)
		if not serviceParam:
			# malformed URL definition
			return HttpResponseServerError("IPTV_ChannelList: can't parse %s", chan.tune)
		
		serviceParam = serviceParam.groupdict()
		
		# generate XML 
		service = ET.Element("SingleService")
		service.attrib['id'] = "%d" % chan.xmltvID
		service.attrib['type'] = 'tv'
		serviceList.append(service)
		
		location = ET.Element("ServiceLocation")
		service.append(location)
		
		mcast = ET.Element("IPMulticastAddress")
		mcast.attrib['Address'] = serviceParam['host']
		mcast.attrib['Port']	= serviceParam['port']
		mcast.attrib['Streaming'] = 'udp'
		location.append(mcast)
		
		rating = ET.Element("Rating")
		rating.attrib['value'] = chan.mpaa
		service.append(rating)
		
		name = ET.Element("TextualIdentifier")
		name.attrib['ServiceName'] = chan.name
		service.append(name)
	
	# or we're done now let's dump out
	
	return HttpResponse(ET.tostring(root, encoding='utf-8'))

@cache_page(60*15)
def GetChannelList(request):
	service = Service.objects.filter(enabled=True, redirect=False)[0]
	
	if service.serviceType == u'DVB':
		return DVB_ChannelList(request)
	elif service.serviceType == u'IPTV':
		return IPTV_ChannelList(request)
	else:
		return HttpResponseServerError("NO ENABLED SERVICE") 

#
# returns Categories assignment, as defined by http://synet.synesis.ru/entries/434740
#
@cache_page(60*15)
def GetChannelCategories(request):
	doc = ET.Element("Categories")
	
	for catL1 in ChannelCategory.objects.all():
		cat1ML = ET.Element("Category"); cat1ML.attrib['name'] = catL1.name; 
		cat1ML.attrib['channel'] = 'true'; cat1ML.attrib['id'] = "%d"%catL1.code
		doc.append(cat1ML)
		
		for gen in catL1.genres.all():
			genML = ET.Element("Category")
			genML.attrib['name'] = gen.name
			cat1ML.append(genML)
		
		for chan in catL1.channels.all():
			chanML = ET.Element("Channel")
			chanML.attrib['id'] = "%d" % chan.xmltvID
			cat1ML.append(chanML)
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))