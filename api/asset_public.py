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
from django.db.models import Min, Max, Sum
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

def LivePlaylist(request, channelXmltvID):
	resp = HttpResponse(mimetype='application/x-mpegURL')
	sums = Chunk.objects.filter(appType=APP_TYPE_NPVR, inAppId=int(channelXmltvID), startTime__gte=(datetime.datetime.utcnow() - datetime.timedelta(minutes=30))).aggregate(Sum('dataBytes'), Sum('durationMs'))
	bandwidth = int(sums['dataBytes__sum']*8000 / sums['durationMs__sum']);
	resp.write("#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=%u\n"% bandwidth)
	resp.write(request.build_absolute_uri("/synet/channels/%s/live/1.m3u8" % channelXmltvID)+'\n')

	return resp;

# if channel is available
# we will generate a playlist for it
def LivePlaylistSpecific(request, channelXmltvID):
	resp = HttpResponse(mimetype='application/x-mpegURL')
	# write header
	headerReady = False

	prevKey = None
	for chunk in Chunk.objects.filter(appType=APP_TYPE_NPVR, inAppId=int(channelXmltvID), startTime__gte=(datetime.datetime.utcnow() - datetime.timedelta(minutes=30))).order_by('startTime'):
		# todo : handle DISCONTINUITY
		if not headerReady:
			resp.write('#EXTM3U\n#EXT-X-TARGETDURATION:%.2f\n#EXT-X-VERSION:2\n#EXT-X-MEDIA-SEQUENCE:%u\n'%(chunk.durationMs/1000.0, chunk.sequenceNumber))
			headerReady = True
		
		if chunk.aesKey != None and chunk.aesKey != '':
			if prevKey is None or prevKey != chunk.aesKey:
				prevKey = chunk.aesKey
				resp.write('#EXT-X-KEY:METHOD=AES-128,URI="%s",IV=0x%s\n'%(request.build_absolute_uri(BASE_URL+'chunk/%d'%chunk.id+'/key'), chunk.aesIV))
		
                resp.write('#EXTINF: %.2f\n'%(chunk.durationMs/1000.0))
		resp.write('%s\n'%chunk.dataUrl)
	
	resp.write('#EXT-X-ENDLIST\n')	
	return resp	
#
# no verification at the moment
#
def HLSPlaylistByAsset(request, assetId):
	resp = HttpResponse(mimetype='application/x-mpegURL')

	# calculate bandwidth - the standard says: 
	# The value is a decimal-integer of bits per second.  It MUST be an
   	# upper bound of the overall bitrate of each media segment (calculated
   	# to include container overhead) that appears or will appear in the playlist
	# 
	# we don't have access to upper bound, but rather sum up an average
	# TODO: review bandwidth calculation
	# 
	totalBytes = 0
	totalSeconds = 0
	for chunk in Chunk.objects.filter(asset__id=int(assetId)).order_by('startTime'):
		totalBytes += chunk.dataBytes
		totalSeconds += chunk.durationMs/1000.0
	 
	resp.write("#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=%u\n"% int((totalBytes*8)/totalSeconds))
	resp.write(request.build_absolute_uri("/synet/asset/%s/play/1"%assetId)+'\n')

	return resp;

def HLSPlaylistSpecificByAsset(request, assetId):
	resp = HttpResponse(mimetype='application/x-mpegURL')
	# write header
	resp.write('#EXTM3U\n#EXT-X-TARGETDURATION:10\n#EXT-X-VERSION:2\n#EXT-X-MEDIA-SEQUENCE:0\n')
	
	prevKey = None
	prevTime = None
	for chunk in Chunk.objects.filter(asset__id=int(assetId)).order_by('startTime'):
		if prevTime and (chunk.startTime - prevTime > datetime.timedelta(milliseconds=chunk.durationMs*1.2)):
			resp.write('EXT-X-DISCONTINUITY\n')
		prevTime = chunk.startTime
		resp.write('#EXTINF: %.2f\n'%(chunk.durationMs/1000.0))
		if chunk.aesKey != None and chunk.aesKey != '':
			if prevKey is None or prevKey != chunk.aesKey:
				prevKey = chunk.aesKey
		
			resp.write('#EXT-X-KEY:METHOD=AES-128,URI="%s",IV=0x%s\n'%(request.build_absolute_uri(BASE_URL+'chunk/%d'%chunk.id+'/key'), chunk.aesIV))
		resp.write('%s\n'%chunk.dataUrl)
	
	resp.write('#EXT-X-ENDLIST\n')
	return resp
