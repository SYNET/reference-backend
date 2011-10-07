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

from django.contrib import admin
from video.models import *
from subscribers.models import Subscriber

# catalog administration

class CategoryInline (admin.TabularInline):
	model 	= Category
	fields 	= ['name', 'countAssets']
	readonly_fields = ['countAssets']
	
	extra 	= 1

class AssetsInline(admin.TabularInline):
	model 	= Asset
	
class CatalogAdmin (admin.ModelAdmin):
	fieldsets = [
		(None,			{'fields': 	[('enabled', 'name')]}),
		('Serving model - either a local service or proxy to other', 	{'fields':	[('model', 'modelProxy')]})
	]
	extra = 1
	#print a
	inlines = [CategoryInline]

admin.site.register(Catalog, CatalogAdmin)

# asset administration

class AssetAdmin (admin.ModelAdmin):
	list_display 	= ['name', 'mpaa', 'category']
	list_filter		= ['category', 'mpaa']
	search_fields 	= ['name']
	save_on_top		= True

admin.site.register(Asset, AssetAdmin)

	