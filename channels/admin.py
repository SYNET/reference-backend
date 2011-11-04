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
from channels.models import Channel, Tariff, ChannelCategory, Genre, DvbMux
from subscribers.models import Subscriber

# ---- TARIFF view 
# ---- comes together with adding / removing channels to tariff
# ---- and allows to browse subscribed users

class ChannelsInline(admin.TabularInline):
	model = Tariff.channels.through # via TariffGroup
	show_url	= True
	ordering 	= ['channel__lcn']

class SubscribersByTariffInline(admin.StackedInline):
	model = Subscriber.tariffs.through # via TariffAssignment
	fields = ['subscriber']
	extra = 0

class TariffAdmin(admin.ModelAdmin)	:
	list_display = ('name', 'enabled', 'cost', 'countSubscribers', 'countChannels')
	inlines = [ChannelsInline, SubscribersByTariffInline]

# ---- CHANNELS view 
# ---- comes together with assigning this channel to specific tariff
class TariffsInline(admin.TabularInline):
	model = Tariff.channels.through
	extra = 1

class ChannelAdmin(admin.ModelAdmin):
	list_display	= ('lcn', 'name', 'xmltvID', 'enabled', 'mpaa')
	list_display_links = ['name']
	search_fields	= ['name']
	fieldsets = [
		(None,		{'fields': [('name', 'enabled', 'npvrEnabled'), ('lcn', 'xmltvID', 'mpaa'), 
								('chanType', 'mux'), ('demoURL'), 
								('mcastAddr', 'mcastPort'), 'tune',]}),
	]
	inlines = [TariffsInline]
	ordering = ['lcn']

class MuxAdmin(admin.ModelAdmin):
	pass;
 
# --- genres assignments --- 
class GenresAdmin(admin.ModelAdmin):
	list_display = ['name']

class GenresInline(admin.TabularInline):
	model = ChannelCategory.genres.through

class ChannelCategoryInline(admin.TabularInline):
	model = ChannelCategory.channels.through
	
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'countChannels', 'countGenres']	
	#fields = ['genres']
	filter_vertical = ('channels',)
	inlines = [GenresInline, ChannelCategoryInline]

admin.site.register(DvbMux, MuxAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(ChannelCategory, CategoryAdmin)
admin.site.register(Genre, GenresAdmin)
