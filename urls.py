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
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^synet/synet_config_ip.xml$', 'api.config.GetConfig'),
	(r'^synet/synet_config_cab_ip_hybrid.xml$', 'api.config.GetConfig'),	
	(r'^synet/channels/list$', 'api.chans.GetChannelList'),
	(r'^synet/channels/categories', 'api.chans.GetChannelCategories'),
	(r'^synet/video/catalog/list', 'api.vodaccess.GetCatalogList'),
	(r'^synet/video/catalog/(?P<catalog_id>\d+)/category/list', 'api.vodaccess.GetCategoriesList'),
	(r'^synet/video/catalog/(?P<catalog_id>\d+)/category/(?P<category_id>\d+)/list/(?P<from_index>\d+)/(?P<limit>\d+)', 'api.vodaccess.GetAssetList'),
	(r'^synet/video/catalog/(?P<catalog_id>\d+)/asset/(?P<asset_id>\d+)/play', 'api.vodaccess.GetAssetPlaylist'),
	
#	(r'^channel/(?P<ch_id>\d+)/read/$', 'channels.view.demoChannel'),		

	# tariffs & activation protocol
	# defined by http://synet.synesis.ru/entries/20004511
	(r'^synet/bill/contract/connect$', 'api.contract.ConnectSTB'),
	(r'^synet/bill/channels/getByPackageId/(?P<package_id>\d+)$', 'api.contract.GetChannelsByPackage'),
	(r'^synet/bill/channels/getByStatus/(?P<enabled_flag>\w+)$', 'api.contract.GetChannelsBySubscriptionStatus'),
	(r'^synet/bill/packages/getByXmltvId/(?P<xmltv_id>\d+)$', 'api.contract.GetPackagesByChannel'),
	(r'^synet/bill/packages/addById/(?P<package_id>\d+)$', 'api.contract.SubscribeToPackage'),
	(r'^synet/bill/packages/deleteById/(?P<package_id>\d+)$', 'api.contract.UnsubscribeFromPackage'),
	(r'^synet/bill/packages/getAll$', 'api.contract.GetAllPackages'),
	
	# subscriber messaging protocol
	# defined by 
	(r'^synet/messages/messageList$', 'api.messages.messageList'),
	(r'^synet/messages/messageText$', 'api.messages.messageView'),
	(r'^synet/messages/messageRead$', 'api.messages.messageRead'),
	
	# administration interface
    url(r'^synet/admin/', include(admin.site.urls)),
)
