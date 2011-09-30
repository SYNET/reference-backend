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

def isMessageRead(readDate):
	if readDate :
		return False
	else:
		return True

def messageList(request):
	resp = HttpResponse(mimetype="text/xml")
	
	stbList = STB.objects.filter(hashKey=request.GET.get("sha1"), 
			macAddr  = request.GET.get("mac"))
	if len(stbList) != 1:
		return HttpResponse("authentication failed", status=404)
	
	doc = ET.Element("messages"); 
	msgList = Message.objects.filter(subscriber=stbList[0].subscriber)
	for m in msgList:
		mX = ET.Element("message")
		mX.attrib['id']	= "%d" % m.id
		mX.attrib['date']	= asctime(m.sendDate.timetuple())
		mX.attrib['read']	= "%s" % isMessageRead(m.readDate)
		subjX = ET.Element("subject")
		subjX.text = m.subject
		mX.append(subjX)
		doc.append(mX)
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

def getMessage(request, msg_id):
	msg = None
	try:
		msg = Message.objects.get(id=msg_id)
	except Exception as a: 
		raise NameError('<error>no such message %s </error>\n' % msg_id)
	
	hashCode = request.GET.get('sha1')
	mac		 = request.GET.get('mac')
	
	if (None == hashCode) | (hashCode == '') | (None == mac) | (None == ''):
		return NameError("messageRead : missing parameters\n")
	
	# validate its coming from correct STB
	validated = False
	for s in msg.subscriber.stb_set.all():
		if (s.hashKey == hashCode) and (s.macAddr == mac):
			return msg;
	raise NameError("<error>validation failed</error>")
	

def messageRead(request, msg_id):
	try:
		msg = getMessage(request, int(msg_id))
	except NameError as e:
		return HttpResponse(content=e, status=404)
	
	msg.readDate = date.today();
	msg.save()
	
	return HttpResponse("<ok/>")

def messageView(request, msg_id):
	msg = None
	try:
		msg = getMessage(request, msg_id)
	except NameError as e:
		return HttpResponse(content=e, status=404)
	
	msgML = ET.Element("message")
	msgML.attrib['id'] = "%d" % msg.id
	msgML.attrib['date'] = asctime(msg.sendDate.timetuple())
	subjML = ET.Element("subject")
	subjML.text = msg.subject
	msgML.text = msg.text
	msgML.append(subjML)
	
	return HttpResponse(ET.tostring(msgML, encoding='utf-8'))
