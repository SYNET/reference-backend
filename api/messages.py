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
# This is an implementation of API between this simple admin and Synet STB
#
from django.http import HttpResponse
from subscribers.models import Subscriber, Message, AccessCard
from synet.models import STB
from django.template import Context, loader
from time import asctime
from datetime import date
from xml.etree import ElementTree as ET
from api import contract

def isMessageRead(readDate):
	if readDate :
		return "true"
	else:
		return "false"

def messageList(request):
	resp = HttpResponse(mimetype="text/xml")
	
	# only access cards are searched
	cards = AccessCard.objects.filter(code=request.GET.get('cardNumber'))
	if len(cards) != 1:
		return contract.billingErrorResponse("User card %s unknown" % request.GET.get('cardNumber'), contract.ERROR_NOT_FOUND)
	
	doc = ET.Element("messages"); 
	msgList = Message.objects.filter(subscriber=cards[0].subscriber)
	for m in msgList:
		mX = ET.Element("message")
		mX.attrib['id']		= "%d" % m.id
		mX.attrib['date']	= asctime(m.sendDate.timetuple())
		mX.attrib['read']	= "%s" % isMessageRead(m.readDate)
		if m.urgent :
			mX.attrib['type'] = 'urgent'
		else:
			mX.attrib['type'] = 'info'
		subjX = ET.Element("subject")
		subjX.text = m.subject
		mX.append(subjX)
		doc.append(mX)
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

def messageRead(request):
	try:
		msg = Message.objects.get(id=int(request.GET.get('msgID')),
					  subscriber__accesscard__code=request.GET.get('cardNumber'))
	except Exception as e:
		return contract.billingErrorResponse(e.__unicode__(), contract.ERROR_NOT_FOUND)
	
	msg.readDate = date.today();
	msg.save()
	
	return HttpResponse("<ok/>")

def messageView(request):
	try:
		msg = Message.objects.get(id=int(request.GET.get('msgID')),
					  subscriber__accesscard__code=request.GET.get('cardNumber'))
	except Exception as e:
		return contract.billingErrorResponse(e.__unicode__(), contract.ERROR_NOT_FOUND)
	
	msgML = ET.Element("message")
	msgML.attrib['id'] = "%d" % msg.id
	msgML.attrib['date'] = asctime(msg.sendDate.timetuple())
	mX.attrib['read']	= "%s" % isMessageRead(m.readDate)
	if m.urgent :
		mX.attrib['type'] = 'urgent'
	else:
		mX.attrib['type'] = 'info'	
	ET.SubElement(msgML, "subject").text = msg.subject
	ET.SubElement(msgML, "text").text=msg.text
	if msg.imageUrl != None and msg.imageUrl != '':
		ET.SubElement(msgML, "img").attrib['url'] = msg.imageUrl
	
	return HttpResponse(ET.tostring(msgML, encoding='utf-8'))
