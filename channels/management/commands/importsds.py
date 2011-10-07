#
# This utility imports legacy IPTV and Hybrid DVB-C SDS files to ease transition
# 
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from channels.models import Channel, DvbMux
from xml.etree import ElementTree as ET

class Command(BaseCommand):
	args = 'file'
	help = 'Imports SDS file into the system'
	
	def handle(self, *args, **options):
		sds = ET.parse(args[0]);
		if sds.getroot().tag == 'Multiplexers':
			self.parseHybrid(sds)
		elif sds.getroot().tag == 'ServiceDiscovery':
			self.parseIPTV(sds)
		else:
			self.stderr.write("*** Unsupported format\n");
	
	def parseHybrid(self, sds):
		xmltvCounter = 5000
		for muxML in sds.getroot().findall("Multiplexer"):
			# create a mux if doesn't exist
			try:
				mux = DvbMux.objects.get(fec_hp = muxML.attrib['fec_hp'],
										 fec_lp = muxML.attrib['fec_lp'],
										 freq	= int(muxML.attrib['freq']),
										 modulation = muxML.attrib['modulation'], 
										 symbolRate = int(muxML.attrib['symbol_rate']))
			except ObjectDoesNotExist:
				mux = DvbMux(fec_hp = muxML.attrib['fec_hp'],
							 fec_lp = muxML.attrib['fec_lp'],
							 freq	= int(muxML.attrib['freq']),
							 modulation = muxML.attrib['modulation'], 
							 symbolRate = int(muxML.attrib['symbol_rate']))
				mux.save()
			
			# populate mux with channels
			for chML in muxML.findall("Service"):
				xmltvML = chML.find("XMLTV"); 
				if xmltvML.attrib['id'] == '--':
					self.stderr.write("* Warn: auto-assign XMLTV ID %d to %s "% (xmltvCounter, chML.find('Name').attrib['name']))
					xmltvID = xmltvCounter
					xmltvCounter += 1
				else:	
					xmltvID = int(xmltvML.attrib['id']); 
				chML.remove(xmltvML)
				try:
					chan = Channel.objects.get(xmltvID=xmltvID)
				except ObjectDoesNotExist:
					chan = Channel()
					chan.xmltvID = xmltvID
				
				nameML 	= chML.find('Name'); chan.name = nameML.attrib['value']; chML.remove(nameML)
				lcnML 	= chML.find('LCN'); chan.lcn = int(lcnML.attrib['value']); chML.remove(lcnML)
				rateML 	= chML.find("Rating")
				if rateML != None:
					chan.mpaa = rateML.attrib['value']
					chML.remove(rateML)
				else:
					chan.mpaa = u'G'
				
				chan.tune = ET.tostring(chML, encoding='utf-8')
				chan.mux  = mux
				chan.mode = u'DVB'
				chan.chanType = chML.attrib['type']
				try :
					chan.save()
				except Exception as e:
					self.stderr.write("Failed to save channel %s, reason %s\n" % (chan, e))

	def parseIPTV(self, sds):
		lcnCount = 0
		for chXML in sds.getroot().findall("BroadcastDiscovery/ServiceList/SingleService"):
			try:
				ch = {}
				ch['xmltvID'] 	= int(chXML.attrib['id'])
				ch['chanType']	= chXML.attrib['type']
				
				mcast 		= chXML.find('ServiceLocation/IPMulticastAddress')
				ch['tune'] 	= "udp://%s:%s" % (mcast.get('Address'), mcast.get('Port'))
				ch['name'] 	= chXML.find('TextualIdentifier').get('ServiceName')
				ch['mpaa']	= chXML.find('Rating')
				if not ch['mpaa']:
					ch['mpaa'] = 'G' # by default - general audiences
				else:
					ch['mpaa'] = ch['mpaa'].get('value')
				
			except Exception as e:
				self.stderr.write("*** Failed to parse %s reason %s" % (ET.tostring(chXML), e))
				continue
			
			lcnCount += 1
			# we don't duplicate records
			if Channel.objects.filter(xmltvID=ch['xmltvID']).count() > 0:
				self.stderr.write(" Channel XMLTV ID=%d already in database, skipping\n" % ch['xmltvID'])
				continue
			
			chanDB = Channel(name		= ch['name'],
						xmltvID		= ch['xmltvID'],
						tune		= ch['tune'],
						chanType	= ch['chanType'],
						mpaa		= ch['mpaa'],
						enabled		= True,
						lcn			= lcnCount,
						mode		= u'IPTV',
						mux			= None
						)
			try:
				chanDB.save()
			except IntegrityError as e:
				print self.stderr.write(u"*** Failed to save channel [%d]%s, reason %s\n" % (chanDB.xmltvID, chanDB.name, e.__unicode__()))
				continue
			
			self.stdout.write(u"added [%d] \n" % chanDB.xmltvID)
			