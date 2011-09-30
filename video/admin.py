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

	