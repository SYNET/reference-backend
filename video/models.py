from django.db import models
from channels.models import MPAA_RATING
from subscribers.models import Subscriber
from video.model_proxies import VOD_MODEL_PROXIES


# VOD service defition:
# Catalog (VOD service)
#  - Category
#   - Assets
#   - Genres (optional)
#
# user actions are logged in Transcations
#

class Asset(models.Model):
	name	= models.CharField("asset conventional name", max_length=100, unique=True)
	mpaa	= models.CharField("asset MPAA rating", max_length=5, choices=MPAA_RATING, blank=True)
#	genres	= models.ManyToManyField('video.Genre', through='video.GenreAssetGroup')
	category= models.ForeignKey('Category')
	imdbID	= models.CharField("IMDB", max_length=40, blank=True)
	playURL = models.URLField("Playlist URL", verify_exists=False, unique=True)
	desc	= models.TextField("Description")
	
	def __unicode__(self):
		return self.name;
	def catalog(self):
		return self.category.catalog
	
# movie poster
class Poster:
	img	= models.FileField("Poster image", upload_to="posters")
	asset	= models.ForeignKey(Asset)

CATALOG_TYPE_CHOICES = (
	(u'local', 	u'Served from local resources'),
	(u'proxy', u'External service accessed via proxy')
)

# VOD instance
class Catalog(models.Model):
	name	= models.CharField("VOD Service name", max_length=100)
	icon	= models.FileField("Catalog icon", upload_to="catalog_icons")
	model	= models.CharField("Local or external", max_length=100, choices=CATALOG_TYPE_CHOICES, default=u'LOCAL')
	modelProxy	= models.CharField("Proxy for external service", max_length=100, choices=VOD_MODEL_PROXIES, blank=True)
	enabled	= models.BooleanField("Enabled", default=True, blank=False)
	
	def __unicode__(self):
		return self.name

# category to store catalog
class Category(models.Model):
	name	= models.CharField("Category", max_length=100)
	catalog	= models.ForeignKey(Catalog)
	
	def countAssets(self):
		return self.asset_set.count()
	
	countAssets.short_description = "# assets"
	
	def __unicode__(self):
		return "%s > %s" % (self.catalog.name, self.name)

class Genre(models.Model):
	name	= models.CharField("Genre", max_length=100)
	category= models.ForeignKey(Category)
	def __unicode__(self):
		return self.name

# association between asset and genre
class GenreAssetGroup(models.Model):
	genre	= models.ForeignKey('channels.Genre')
	asset	= models.ForeignKey('Asset')

class Transaction(models.Model):
	tstamp	= models.DateField('Date', editable=False)
	asset	= models.ForeignKey(Asset, editable=False)
	subscriber	= models.ForeignKey(Subscriber, editable=False)
