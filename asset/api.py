#
# PUBLIC API
# 
# GetPlaylist()
#
# INTERNAL API 
# 
# AssetCreated()
# AssetRemoved()

#
# Returns a playlist according to client's entitlement
#
def GetPlaylist(request, entitlementSerial):

# 
# This call is should be initiated by transcoder / segmenter
# identifying that a specific chunk has been created
def ChunkCreated(request, apiKey, aesKey, aesIV, sequenceNumber, durationMs):
	if not clientValid(apiKey): 
		return HttpServerResponse(msg="Invalid API key", code=500)
	
	try:
		Chunk(sequenceNumber	= int(sequenceNumber),
				durationMs		= int(durationMs),
				aesKey			= aesKey, 
				aesIV			= aesIV,
				groupID			= request.GET.get("groupID"),
				storeUrl	 	= request.GET.get("storeUrl")).save()
	except Exception as e:

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
	except Exception e: 
		return apiError("Error creating asset")

	return apiOK()
