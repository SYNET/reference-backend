# SYNET Interactive TV Middleware Reference Backend Application
#
# Copyright SYNESIS 2001
# www.synesis.ru
# 
# You are free to use this software as long as it is only 
# used together with set top boxes equipped with SYNET embedded middleware
#

from django.http import HttpResponse, HttpResponseRedirect
from xml.etree import ElementTree as ET
from synet.models import Service, STB
from subscribers.models import Subscriber
from channels.models import Channel, Tariff
import re

#
# checks if version needs upgrade
# 
versionRE = re.compile("(?P<p1>[0-9]+)\.(?P<p2>[0-9]+)\.(?P<p3>[0-9]+)")

def needUpgrade(cur, newFw):
	if not newFw:
		return False
	
	curVer = versionRE.match(cur)
	newVer = versionRE.match(newFw.version)
	
	if not curVer or not newVer:
		raise Exception("can't parse versions %s,%s"%(cur, newFw.version))
	
	curVer = curVer.groupdict()
	newVer = newVer.groupdict()
	
	if int(newVer['p1']) > int(curVer['p1']):
		return True
	if int(newVer['p2']) > int(curVer['p2']):
		return True
	if int(newVer['p3']) > int(curVer['p3']):
		return True
	
	return False

# 
# STB inquires a configuration URL depending on HW/SW configuration
# 
def GetConfig(request):
	# if this STB has a special service, redirect it there
	try:
		stb = STB.objects.get(macAddr=request.GET.get('mac'))
		if stb.service: 
			if stb.service.redirect:
				return HttpResponseRedirect(stb.service.redirectURL)
	except Exception: pass;
	
	# identify an active Service configuration
	service = Service.objects.filter(enabled=True, redirect=False)[0]
	
	currentVersion = request.GET.get('sw_ver')
	
	# generate config
	config = ET.Element("config")
	
	if Tariff.objects.filter(enabled=True).count() > 0:
		bill = ET.Element("BILLING")
		bill.attrib['url'] = 'http://synet.local/synet/bill'
		config.append(bill)
	
	p = ET.Element("SDS")
	p.attrib['url'] = 'http://synet.local/synet/channels/list'
	config.append(p)
	
	p = ET.Element("CAT")
	p.attrib['url'] = 'http://synet.local/synet/channels/categories'
	config.append(p)
	
	p = ET.Element("XMLTV")
	p.attrib['url'] = service.epgServerUrl
	config.append(p)
	
	p = ET.Element("region")
	p.attrib['locale'] 	= service.hmiLocale
	p.attrib['timezone'] = service.timeZone
	config.append(p)
	
	p = ET.Element('NTP')
	p.attrib['addr'] = service.ntpAddr
	config.append(p)
	
	if service.autoTuneChan:
		p = ET.Element('tune')
		p.attrib['channel'] = "%d" % service.autoTuneChan.xmltvID
		config.append(p)
	
	if service.igmpVersion:
		p = ET.Element('IGMP')
		p.attrib['version'] = "%d" % service.igmpVersion
		config.append(p)
	
	# now we need to check if we need to push to more recent version
	if needUpgrade(currentVersion, service.currentFW):
		p = ET.Element("update")
		p.attrib['url'] 	= service.currentFW.url
		if service.forceFWUpdate:
			p.attrib['force']	= 'yes'
		p.attrib['version']	= service.currentFW.version
		config.append(p)
	
	return HttpResponse(ET.tostring(config, encoding='utf-8'))
