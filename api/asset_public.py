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
from asset.models import Chunk, APP_TYPE_NPVR
import binascii
import datetime

logger = logging.getLogger(__name__)

BASE_URL = '/synet/asset/'

def KeyByChunk(request, chunkId):
	resp = HttpResponse(mimetype='binary/octet-stream')
	resp.write(binascii.unhexlify(Chunk.objects.get(id=int(chunkId)).aesKey))
	
	return resp

# if channel is available
# we will generate a playlist for it
def LivePlaylist(request, channelXmltvID):
	resp = HttpResponse(mimetype='application/x-mpegURL')
	# write header
	headerReady = False

	prevKey = None
	for chunk in Chunk.objects.filter(appType=APP_TYPE_NPVR, inAppId=int(channelXmltvID), startTime__gte=(datetime.datetime.utcnow() - datetime.timedelta(minutes=30))).order_by('startTime'):
		# todo : handle DISCONTINUITY
		if not headerReady:
			resp.write('#EXTM3U\n#EXT-X-TARGETDURATION:%.2f\n#EXT-X-VERSION:2\n#EXT-X-MEDIA-SEQUENCE:%.2f\n'%(chunk.durationMs/1000.0, chunk.sequenceNumber))
			headerReady = True
		
		resp.write('#EXTINF: %.2f\n'%(chunk.durationMs/1000.0))
		if chunk.aesKey != None and chunk.aesKey != '':
			if prevKey is None or prevKey != chunk.aesKey:
				prevKey = chunk.aesKey
				resp.write('#EXT-X-KEY:METHOD=AES-128,URI="%s"\n'%request.build_absolute_uri(BASE_URL+'chunk/%d'%chunk.id+'/key'))
		resp.write('%s\n'%chunk.dataUrl)
	
	return resp	
#
# no verification at the moment
#
def PlaylistByAsset(request, assetId):
	resp = HttpResponse(mimetype='application/x-mpegURL')
	# write header
	resp.write('#EXTM3U\n#EXT-X-TARGETDURATION:10\n#EXT-X-VERSION:2\n#EXT-X-MEDIA-SEQUENCE:0\n')
	
	prevKey = None
	for chunk in Chunk.objects.filter(asset__id=int(assetId)).order_by('startTime'):
		resp.write('#EXTINF: %.2f\n'%(chunk.durationMs/1000.0))
		if chunk.aesKey != None and chunk.aesKey != '':
			if prevKey is None or prevKey != chunk.aesKey:
				prevKey = chunk.aesKey
				resp.write('#EXT-X-KEY:METHOD=AES-128,URI="%s"\n'%request.build_absolute_uri(BASE_URL+'chunk/%d'%chunk.id+'/key'))
		resp.write('%s\n'%chunk.dataUrl)
	
	resp.write('#EXT-X-ENDLIST\n')
	return resp
