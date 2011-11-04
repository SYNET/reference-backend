from django.db import models
from django.db.models import Sum

# Assets are stored as segmented files
# the API is used to provide URL for playback

APP_TYPE_VOD = 1
APP_TYPE_NPVR = 2

APPLICATION_TYPE = (
	(APP_TYPE_VOD, 'Video on Demand'),
	(APP_TYPE_NPVR, 'Network PVR')
)

#
# don't maintain excess integrity as data is not stored forever
# just keeping indexes of initial and subsequent 
class Asset(models.Model):
	dataBytes		= models.BigIntegerField("how many bytes in total in that asset")
	durationMs		= models.PositiveIntegerField("how many milliseconds in that asset")
	markToDelete	= models.BooleanField("schedule asset to delete", default=False)

	# this call requires all chunks to be already associated with this asset (i.e. saved)
	def calculateBandwidth(self):
		cnt = Chunk.objects.filter(asset=self).aggregate(Sum('dataBytes'), Sum('durationMs'));
		self.dataBytes = cnt['dataBytes__sum']
		self.durationMs	= cnt['durationMs__sum']
	
class Chunk(models.Model):
	# sequence number could be restarted and rolled around
	# i.e. for a single broadcast channel when transcoder restarts
	sequenceNumber	= models.IntegerField("chunk sequence #, this is assigned automatically")
	# group ID could be something which is used later to create an asset
	# and join chunks
	appType			= models.IntegerField("to which application the chunk belongs to", choices=APPLICATION_TYPE)
	inAppId			= models.IntegerField("internal ID to application - i.e. xmltvID of channel in NPVR", max_length=20, blank=False)
	durationMs		= models.IntegerField("duration in millisconds", blank=False, null=False)
	startTime		= models.DateTimeField("start time, none if not for live stream", blank=True, null=True)
	asset			= models.ForeignKey("Asset", on_delete=models.SET_NULL, blank=True, null=True)
	dataUrl			= models.URLField("data location URL", blank=False, null=False)
	dataBytes		= models.PositiveIntegerField("size of data chunk", blank=False, null=False)
	
	# stores decryption keys
	aesKey			= models.CharField('AES-CBC-128 key', max_length=48)
	aesIV			= models.CharField('AES key init vector', max_length=48)
	
	class Meta:
		unique_together = (('sequenceNumber', 'appType', 'inAppId', 'startTime', 'dataUrl'))

# entitlement is obtained while purchase
# and used to validate client's requests
class Entitlement(models.Model):
	effectiveFrom	= models.DateTimeField()
	effectiveTo		= models.DateTimeField()
	clientIP		= models.IPAddressField()
	asset			= models.ForeignKey(Asset)

class ApiKeys(models.Model):
	name			= models.CharField("Name", max_length=20, blank=False)
	key				= models.CharField("Name", max_length=20, blank=False)
