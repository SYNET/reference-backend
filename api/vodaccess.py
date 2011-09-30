# 
# This is an api to serve locally managed media catalogs
# For external catalogs, set up a proxy: see video.model_proxies
#
from video.models import *
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from xml.etree import ElementTree as ET

MAX_ASSET_LIMIT = 100

#
# - catalog list
# - list files in catalog with paging
# - format is XML
# 

# returns list of enabled catalogs
@cache_page(60*15)
def GetCatalogList(request):
	doc = ET.Element("Catalogs")
	for cat in Catalog.objects.filter(enabled=True):
		catML 					= ET.Element("Catalog")
		catML.attrib['id']	= "%d"%cat.id
		catML.text 	= cat.name
		doc.append(catML)
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

# 
# returns list of category in given catalog
# 
@cache_page(60*15)
def GetCategoriesList(request, catalog_id):
	doc = ET.Element("Categories")
	
	for cat in Catalog.objects.get(pk=catalog_id).category_set.all():
		catML = ET.Element("Category")
		catML.attrib['id']		= "%d"%cat.pk
		catML.attrib['total'] 	= "%d"%Asset.objects.filter(category=cat.pk).count()
		catML.text				= cat.name
		doc.append(catML)
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

#
# get asset list in given catalog and category
#
@cache_page(60*15)
def GetAssetList(request, catalog_id, category_id, from_index, limit):
	doc = ET.Element("Assets")
	
	from_index	= int(from_index); limit = int(limit)
	
	if limit > MAX_ASSET_LIMIT:
		limit = MAX_ASSET_LIMIT
	
	cnt = 0
	for asset in Asset.objects.filter(category=category_id)[from_index-1:from_index+limit]:
		asML = ET.Element("Asset")
		asML.attrib['id'] 	= "%d"%asset.id
		asML.attrib['mpaa']	= asset.mpaa
		asML.attrib['name']	= asset.name
		asML.text			= asset.desc
		doc.append(asML)
		cnt += 1
	
	if cnt == 0:
		doc.attrib['fromIndex'] = "-1"
		doc.attrib['toIndex']	= "-1"
	else:
		doc.attrib['fromIndex'] = "%d" % from_index
		doc.attrib['toIndex']	= "%d" % (from_index+cnt-1)
	doc.attrib['total']		= "%d" % Asset.objects.filter(category=category_id).count()
	
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))

#
# Returns actual playlist
# This call is required to be authenticated
#
def GetAssetPlaylist(request, catalog_id, asset_id):
	#from contract import GetSubscriber, SubscriberNotAuthenticated
	
	asset = Asset.objects.get(pk=asset_id)
	
	doc = ET.Element("Playlist"); doc.attrib['url'] = asset.playURL
	return HttpResponse(ET.tostring(doc, encoding='utf-8'))