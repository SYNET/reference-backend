#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2011 Synesis LLC.
#
# Technical support and updates: http://synet.synesis.ru
# You are free to use this software for evaluation and commercial purposes
# under condition that it is used only in conjunction with digital TV
# receivers running SYNET middleware by Synesis.
# 
# To contribute modifcations, additional modules and derived works please
# contact synet@synesis.ru

import sys
import binwriter
import epg.server_helper as server_helper
import epg.server_plain_req as server_plain_req
import epg.server_ctg_req as server_ctg_req
from   django.http import HttpResponse
from   django.db import connections

MAX_LIMIT = 100

def queryset2dict(q):
	d = {}
	for k in q.keys():
		d[k] = q.getlist(k)
	
	return d

def ServeRequest(request, outputFormat):
	writers = {
		'epg' : binwriter.row2bin,
		'epg_py' : lambda row: '%s\n' % row,
	}
	content_types = {
		'epg' : 'application/octet-stream',
		'epg_py' : 'text/plain',
	}
	
	query_db = server_plain_req.query_db
	if 'ctg_id' in request.GET:
		query_db = server_ctg_req.query_db
	
	if outputFormat not in ('epg', 'epg_py'):
		return HttpResponse("wrong output format", code=404)
    
	for param in request.GET.keys():
			if not param in server_helper.where_params and \
				not param in server_helper.paging_params and \
				not param in server_helper.other_params:
					return False;
	
	response = HttpResponse(content_type=content_types[outputFormat])
	
	if 'limit' in request.GET and int(request.GET.get('limit')) > server_helper.limit_max:
		request.GET['limit'] = [ str(MAX_LIMIT) ]
	rows = query_db(connections['epg'].cursor(), queryset2dict(request.GET))
	writer = writers[outputFormat]
	for row in rows:
		response.write(writer(row))
	
	return response;
