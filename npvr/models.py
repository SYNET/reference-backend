from django.db import models
from asset.models import Asset
from channels.models import Channel

# 
# Defines an NPVR record
#
class NpvrRecord(Asset):
	channel		= models.ForeignKey(Channel)
	airTime		= models.DateTimeField("Air time")
	durationSec	= models.PositiveIntegerField()
	title		= models.CharField(max_length=256)
	description	= models.TextField()
	catalogID	= models.PositiveIntegerField("Catalog ID for repeating programs, assigned by EPG vendor", blank=True, null=True, default=None)
	posterUrl	= models.URLField(blank=True, null=True, default=None)

# there should be just one pair of channel and time
class NpvrRecordsStatistics(models.Model):
	channel		= models.ForeignKey(Channel)
	lastTime	= models.DateTimeField("Last timepoint which was processed for this channel")
	
