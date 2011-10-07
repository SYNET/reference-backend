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
from synet.models import Service, Firmware, STB

class STB_Inline(admin.TabularInline):
	model = STB
	fields = ['macAddr', 'fwVersion', 'hashKey']
	readonly_fields = ['macAddr', 'fwVersion', 'hashKey']
	extra = 0
	canDelete = True

class StbAdmin(admin.ModelAdmin):
	list_display = ['macAddr', 'fwVersion', 'hashKey', 'subscriber']
	fields = ['macAddr', 'hashKey', 'fwVersion', 'subscriber', 'service']
	readonly_fields = ['fwVersion']

class ServiceAdmin(admin.ModelAdmin):
	list_display	= ['name', 'enabled']
	
	fieldsets = [
		(None,			{'fields': 	[('enabled', 'name', 'serviceType')]}),
		('Firmeware', 	{'fields':	[('forceFWUpdate', 'currentFW')],
						 'description': 'Firmwares'}),
		('Regional settings', {'fields': [('timeZone', 'hmiLocale')]}),
		('Other services',  {'fields': [('epgServerUrl', 'statServerUrl')],
							 'description': ['Leave blank to disable']}),
#		('Tariff management', {'fields': [('billingMode', 'billingForwardingURL')]}),
		('Automatic channel tuning on STB statr-up', {'fields': ['autoTuneChan']}),
		('IPTV settings (only required for IPTV and OTT service type)', 
						{'fields': [('igmpVersion', 'ntpAddr')]}),
		('Redirect to another config URL', {'fields': [('redirect', 'redirectURL')]}),
	]
	
	#filter_horizontal = ['stb_set']
	inlines = [STB_Inline]

class FirmwareAdmin(admin.ModelAdmin):
	list_display	= ['version', 'countUsage','url']

admin.site.register(Service, ServiceAdmin)
admin.site.register(Firmware, FirmwareAdmin)
admin.site.register(STB, StbAdmin)