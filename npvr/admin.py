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
from npvr.models import NpvrRecord

class RecordAdmin (admin.ModelAdmin):
	list_display 	= ['airTime', 'title', 'channel']
	list_filter		= ['channel']
	search_fields 	= ['title', 'description', 'channel__name']
	save_on_top		= True

admin.site.register(NpvrRecord, RecordAdmin)