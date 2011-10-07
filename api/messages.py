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
from subscribers.models import Subscriber, Message
from synet.models import STB
from django.template import Context, loader
from time import asctime
from datetime import date
from xml.etree import ElementTree as ET
from api import contract

def isMessageRead(readDate):
	if readDate :
		return False
	else:
		return True

def messageList(request):
	resp = HttpResponse(mimetype="text/xml")
	
	stbList = STB.objects.filter(hashKey=request.GET.get("sha1"))
	if len(stbList) != 1:
		# no pairing, request it
		return contract.billingErrorResponse("Pairing required", contract.ERROR_NEED_PAIRING)
	
	doc = ET.Element("messages"); 
	msgList = Message.objects.filter(subscriber=stbList[0].subscriber)
	for m in msgList:
		mX = ET.Element("message")
		mX.attrib['id']		= "%d" % m.id
		mX.attrib['date']	= asctime(m.sendDate.timetuple())
		mX.attrib['read']	= "%s" % isMessageRead(m.readDate)
		subjX = ET.Element("subject")
		subjX.text = m.subject
		mX.append(subjX)
		doc.append(mX)
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

def messageRead(request):
	try:
		msg = Message.objects.get(id=int(request.GET.get('msgID')),
					  subscriber__accesscard__code=request.GET.get('cardNumber'),
					  subscriber__stb__hashKey=request.GET.get('sha1'))
	except Exception as e:
		return contract.billingErrorResponse(e.__unicode__(), contract.ERROR_NOT_FOUND)
	
	msg.readDate = date.today();
	msg.save()
	
	return HttpResponse("<ok/>")

def messageView(request):
	try:
		msg = Message.objects.get(id=int(request.GET.get('msgID')),
					  subscriber__accesscard__code=request.GET.get('cardNumber'),
					  subscriber__stb__hashKey=request.GET.get('sha1'))
	except Exception as e:
		return contract.billingErrorResponse(e.__unicode__(), contract.ERROR_NOT_FOUND)
	
	msgML = ET.Element("message")
	msgML.attrib['id'] = "%d" % msg.id
	msgML.attrib['date'] = asctime(msg.sendDate.timetuple())
	ET.SubElement(msgML, "subject").text = msg.subject
	ET.SubElement(msgML, "text").text=msg.text
	
	return HttpResponse(ET.tostring(msgML, encoding='utf-8'))
