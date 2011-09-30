from django.contrib import admin
from channels.models import Channel, Tariff, ChannelCategory, Genre
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
		(None,		{'fields': [('name', 'enabled'), ('lcn', 'xmltvID', 'mpaa'), ('chanType', 'mode', 'mux'), 'tune']}),
	]
	inlines = [TariffsInline]
	ordering = ['lcn']

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

admin.site.register(Channel, ChannelAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(ChannelCategory, CategoryAdmin)
admin.site.register(Genre, GenresAdmin)
