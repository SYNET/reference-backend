# INTERNAL API to be used by utilities which create data
#
# AssetCreated()
# AssetRemoved()
from django.http import HttpResponse, HttpResponseServerError
from asset.models import Chunk
from datetime import datetime

# 
# checks if client is valid
#
def clientValid(apiKey):
	return apiKey == settings.SYNET_API_KEY

#
# Returns a playlist according to client's entitlement
#
def GetPlaylist(request, entitlementSerial):
	pass
# 
# This call is should be initiated by transcoder / segmenter
# the following parameters are received : 
# 'channelXmltvID' 
# 'sequence'	 
# 'startTimeEpoch' 
# 'duration'	 
# 'aesKey'		 
# 'aesIV',		 
# 'file'		

def ChunkCreated(request):
	if not clientValid(request.GET.get('apiKey')): 
		return HttpResponse("Invalid API key", status=404)
		
	try:
		Chunk(sequenceNumber	= int(request.GET.get('sequence')),
				startTime		= datetime.utcfromtimestamp(int(float(request.GET.get('startTimeEpoch')))),
				durationMs		= int(float(request.GET.get('duration'))*1000),
				appType			= int(request.GET.get('appType')),
				inAppId			= int(request.GET.get('channelID')),
				aesKey			= request.GET.get('aesKey'), 
				aesIV			= request.GET.get('aesIV'),
				dataUrl			= request.GET.get('file')
		).save()
	except Exception as e:
		return HttpResponse(e, status=500)
	
	return HttpResponse('OK')

# 
# only for live streams, as fixed assets would have NULL startTime
#
def CreateAssetByTime(request, timeFrom, timeTo):
	groupID = request.GET.get("groupID")
	chunks = Chunk.objects.filter(groupID = groupID).order_by("startTime")
	if chunks.count() == 0:
		# oops, nothing is found, nothing is created
		return apiError("No suitable elements found", code=NOT_AVAILABLE)
	
	minIdx = maxIdx = chunks[0]
	for c in chunks[1:]: 
		if c.sequenceNumber > maxIdx.sequenceNumber: maxIdx = c.sequenceNumber
		if c.sequenceNumber < minIdx.sequenceNumber: minIdx = c.sequenceNumber
	
	try :
		Asset(reason 		= "CreateAssetByTime(%s, [%s:%s])" % (groupID, timeFrom, timeTo),
			chunkFrom	= minIdx,
			chunkTo		= maxIdx,
			creationDate= datetime.now()).save()
	except Exception as e: 
		return apiError("Error creating asset")

	return apiOK()
