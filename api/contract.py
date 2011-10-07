# coding=utf-8
#
# Implements parts of BILLING API, as defined by http://synet.synesis.ru/entries/20004511
#
from django.http import HttpResponse
from django.template import Context, loader
from time import asctime
from datetime import date
from subscribers.models import Subscriber, Message
from synet.models import Service, STB
from subscribers.models import Subscriber, AccessCard
from channels.models import Channel, Tariff, TariffGroup, TariffAssignments
import logging
from xml.etree import ElementTree as ET

# 400 - доступ запрещен - например, неверный пин-код, итд. 
# 500 - внутренняя ошибка сервера
# 404 - не найден (пакет, канал, пользователь, итд)
# 405 - пакет или канал не совместим с текущей подпиской
# 409 - уже существует - попытка повторно подписаться (отписаться) от пакета
# 411 - приемник не прошел процедуру пэйринга между сервером и STB. В случае получения данного кода, отображается экран ввода пин-кода пользователем, после чего приемник
ERROR_ACCESS_DENIED = 400
ERROR_INTERNAL		= 500
ERROR_NOT_FOUND		= 404
ERROR_INCOMPATIBLE	= 405
ERROR_ALREADY_EXISTS= 409
ERROR_NEED_PAIRING	= 411

#
# two variables below define formatting on STB to render 
XML_FORMATTING_PACKAGES = ET.parse('api/XML_FORMATTING_PACKAGES.xml').getroot()
XML_FORMATTING_CONTRACT = ET.parse('api/XML_FORMATTING_CONTRACT.xml').getroot()
OK_PACKAGE_SUBSCRIBED 	= u'Package added to subscription'
OK_PACKAGE_UNSUBSCRIBED = u'Package unsubscribed'
#
# Standard error response for STB
#
def billingErrorResponse(msg, code):
	doc = ET.Element("error")
	codeML = ET.Element("code"); codeML.text = "%d"%code; doc.append(codeML)
	msgML = ET.Element("msg"); msgML.text = msg; doc.append(msgML)
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

def billingOKResponse(msg):
	doc = ET.Element("response")
	ET.SubElement(doc, 'success').text = 'true'
	ET.SubElement(doc, 'msg').text = msg
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

# exception chain
class SynetException(Exception):
	def __init__(self, msg):
		self.msg = msg
		logging.getLogger("SYNET").error(msg)
	def __str__(self):
		return repr(self.msg)

#
# exception to identify that subscriber cannot be authenticated using HTTP request parameters
#
class SubscriberNotAuthenticated(SynetException):
	def __init__(self, msg, code):
		self.resp = billingErrorResponse(msg, code)
		super(SubscriberNotAuthenticated, self).__init__(msg)

# returns subscriber or raises exception
# it assumes that subscriber's STB is already authenticated

def getSubscriber(request):
	cardNum = request.GET.get('cardNumber')
	cards = AccessCard.objects.filter(code=cardNum, enabled=True)
	if cards.count() == 0:
		raise SubscriberNotAuthenticated("Card %s not found"%cardNum, ERROR_ACCESS_DENIED)
	elif cards.count() > 1:
		raise SubscriberNotAuthenticated("Multiple cards found, contact administrator", ERROR_ACCESS_DENIED)
	
	# card found, check if STB is paired with subscriber
	stbs = cards[0].subscriber.stb_set.filter(hashKey=request.GET.get('sha1'))
	if stbs.count() == 0: # STB is not bound to subscriber, request pairing
		raise SubscriberNotAuthenticated("Need pairing", ERROR_NEED_PAIRING)
	elif stbs.count() > 1:
		return SubscriberNotAuthenticated("Multiple STBs found", ERROR_ACCESS_DENIED)
	
	return cards[0].subscriber

# this request returns list of enabled channels for a given subscriber
# /channels/getByStatus/enabled?sha1=XXXX&cardNumber=ABCDE
#
def GetChannelsBySubscriptionStatus(request, enabled_flag):
	try:
		sub = getSubscriber(request)
	except SubscriberNotAuthenticated as err:
		return err.resp
	
	if bool(enabled_flag):
		chans = Channel.objects.filter(enabled=True, tariff__subscriber=sub).only('xmltvID')
	else:
		chans = Channel.objects.filter(enabled=True).exclude(tariff__subscriber=sub).only('xmltvID')
	
	# write out
	resp = HttpResponse()
	resp.write(u'<channels>\n')
	for ch in chans:
		resp.write(u' <xmltvId>%d</xmltvId>\n' % ch.xmltvID)
	resp.write(u'</channels>\n')
	
	return resp 
#
# /channels/getByPackageId/<id>
#
def GetChannelsByPackage(request, package_id):
	try:
		sub = getSubscriber(request)
	except SubscriberNotAuthenticated as err:
		return sub.resp

	try:
		tariff = Tariff.objects.get(pk=package_id)
	except Tariff.DoesNotExist as e:
		return billingErrorResponse(msg="No such tariff", code=ERROR_ACCESS_DENIED)
	
	doc = ET.Element("channels")
	for chan in tariff.objects.channels.filter(enabled=True):
		ET.SubElement(doc, 'xmltvid')
		doc.append(ET.Element('xmltvId', attrib={}, text="%d"%chan.xmltvID))
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

#
# Serves /packages/getAll call
# no authentication, as tariff (package) plan is the same for all subscribers
#
def GetAllPackages(request):
	try: 
		sub = getSubscriber(request)
	except SubscriberNotAuthenticated as err:
		return err.resp
	
	doc = ET.Element("packages")
	
	subscriptions = sub.tariffassignments_set.all()
			
	for pack in Tariff.objects.filter(enabled=True):
		packML = ET.SubElement(doc, "package")
		# search within subscriptions for this given package
		if len(filter(lambda ta : ta.tariff == pack, subscriptions)) > 0:
			ET.SubElement(packML, 'subscribed').text = 'true'
		else:
			ET.SubElement(packML, 'subscribed').text = 'false'
		ET.SubElement(packML, 'available').text = 'true'
		ET.SubElement(packML, 'id').text = "%d"%pack.pk
		ET.SubElement(packML, 'name').text = pack.name
		ET.SubElement(packML, 'price').text = pack.cost
		
		chanML = ET.SubElement(packML, 'channels')
		for chan in pack.channels.all(): 
			ET.SubElement(chanML, 'xmltvid').text = "%d"%chan.xmltvID
	
	resp = ET.Element('packages')
	resp.append(XML_FORMATTING_PACKAGES)
	resp.append(doc)
	return HttpResponse(ET.tostring(resp, encoding='utf-8'))
#
# /paсkages/addById/24
# 
def SubscribeToPackage(request, package_id):
	try:
		sub = getSubscriber(request)
	except SubscriberNotAuthenticated as err:
		return sub.resp
	
	tariff = Tariff.objects.get(pk=int(package_id))
	# check this assignment already exists
	try:
		assignments = sub.tariffassignments_set.get(tariff = tariff)
		# do nothing, it's already there
	except TariffAssignments.DoesNotExist as err:
		TariffAssignments(subscriber=sub, tariff = tariff).save()
	
	return billingOKResponse(OK_PACKAGE_SUBSCRIBED)

#
# /paсkages/deleteById/24
# 
def UnsubscribeFromPackage(request, package_id):
	try:
		sub = getSubscriber(request)
	except SubscriberNotAuthenticated as err:
		return sub.resp
	
	# check this assignment already exists
	try:
		sub.tariffassignments_set.get(tariff__pk=int(package_id)).delete()
	except TariffAssignment.DoesNotExist as err:
		# it's not there, do nothing
		pass

	return billingOKResponse(OK_PACKAGE_UNSUBSCRIBED)

#
# this call serves /paсkages/getByXmltvId/101 request to fetch all tariffs (packages) by given channel ID
# and appends formatting 
#<packages>
#	<package>
#		<subscribed>true</subscribed>
#		<available>true</available>
#		<id>101</id>
#		<name>&#x414;&#x440;&#x443;&#x437;&#x44C;&#x44F;</name>
#		<price>50 (1.70)</price>
#		<channels>
#			<xmltvId>123</xmltvId>
#			<xmltvId>124</xmltvId>
#			<xmltvId>125</xmltvId>
#		</channels>
#	</package>
# <totalPrice>50 EUR</totalPrice>
#</packages>
#
def GetPackagesByChannel(request, xmltv_id):
	try:
		subscriber = getSubscriber(request)
	except SubscriberNotAuthenticated as err:
		return err.resp
	
	doc = ET.Element("packages")
		
	subscribedTariffs = subscriber.tariffs.all()
	allTariffs = TariffGroup.objects.filter(tariff__enabled=True, channel__xmltvID=int(xmltv_id)).all()
	
	for ta in allTariffs:
		pML = ET.Element("package"); doc.append(pML)
		subML = ET.Element("subscribed"); pML.append(subML)
		if ta.tariff in subscribedTariffs:
			subML.text = 'true'
		else:
			subML.text = 'false'
		ET.SubElement(pML, 'id').text 	= "%d"%ta.tariff.pk
		ET.SubElement(pML, 'name').text	= ta.tariff.name
		ET.SubElement(pML, 'price').text= ta.tariff.cost
		
		chansML = ET.SubElement(pML, 'channels')
		
		for chan in ta.tariff.channels.filter(enabled=True):
			ET.SubElement(chansML, 'xmltvId').text = "%d"%chan.xmltvID
	
	resp = ET.Element("packages")
	resp.append(XML_FORMATTING_PACKAGES)
	resp.append(doc)
	return HttpResponse(ET.tostring(resp, encoding='utf-8'))

# the call passes request for initial validation
# /contract/connect?mac=00:00:00:00:01&sha1=XXXXXXX&cardNumber=ABCDE&pin=391
# 
# if no such STB exists, we register it
# if there's already such STB (identified by sha1 parameter), we update its information
# 
def ConnectSTB(request):
	sha1 = request.GET.get('sha1')
	mac		 = request.GET.get('mac')
	cardNum  = request.GET.get('cardNumber')
	pin 	 = request.GET.get('pin')
	
	subs 	= Subscriber.objects.filter(accesscard__code=cardNum,
		 								accesscard__pin=pin,
										accesscard__enabled=True)
	if subs.count() != 1:
		return billingErrorResponse(msg="Wrong PIN", code=ERROR_ACCESS_DENIED)
	
	# check STB
	stbList	= STB.objects.filter(subscriber=subs[0], hashKey=sha1)
	if stbList.count() == 0:
		# new STB, let's activate it
		fwv=request.GET.get('SW_VERSION')
		if not fwv:
			fwv = '0.0.0'
		stb = STB(subscriber=subs[0], macAddr=mac, hashKey=sha1, fwVersion=fwv)
		stb.save()
		return HttpResponse("<response><success>true</success></response>\n")
	elif stbList.count() == 1:
		return HttpResponse("<response><success>true</success></response>\n")
	else:
		return billingErrorResponse(msg="Wrong STB registration please contact administrator", code=ERROR_ACCESS_DENIED)
