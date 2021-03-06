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

from subscribers.models import Subscriber, Message, AccessCard
from synet.models import STB
from channels.models import Tariff
from video.models import Transaction
from django.contrib import admin

class STB_Inline(admin.TabularInline):
	model = STB
	fields = ['macAddr', 'fwVersion', 'hashKey']
	readonly_fields = ['macAddr', 'fwVersion', 'hashKey']
	extra = 1
	canDelete = False

class AccessCardsInline(admin.TabularInline):
	model 	= AccessCard
	extra	= 0

class MessageInline(admin.TabularInline):
	model = Message
	fields = ['urgent', 'sendDate', 'isRead', 'subject', 'text', 'imageUrl']
	readonly_fields = ['isRead']
	extra = 1
	original = None

class TariffsInline(admin.TabularInline):
	model = Subscriber.tariffs.through
	can_delete	= True

# view transactions by subscribers
class TransactionsInline (admin.TabularInline):
	model 		= Transaction
	fields 		= ['asset', 'tstamp']
	readonly_fields = ['asset', 'tstamp']
	ordering	= ['tstamp']
	extra		= 0
	list_editable = False
	can_delete  = False
	
	def has_add_permission(self, request):
		return False
	
class SubscriberAdmin(admin.ModelAdmin):
	list_display	= ['name', 'receivesService']
	
	fieldsets = [
		(None,		{'fields': ['name']}),
	]
	inlines = [AccessCardsInline, STB_Inline, MessageInline, TariffsInline, TransactionsInline]
	
	actions = ['clearMessages']
	
	def clearMessages(self, request, queryset):
		for m in queryset:
			m.message_set.all().delete()
		self.message_user(request, "Cleared selected subscriber's messages")
#
#
#
admin.site.register(Subscriber, SubscriberAdmin)


