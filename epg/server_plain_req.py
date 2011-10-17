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
# contact pnx@synesis.ru

import server_helper

def make_where_str(http_req_args, db_req_args):
    where_str = ''
    for param in http_req_args.keys():
        if param in server_helper.where_params:
            if where_str != '':
                where_str += ' AND '

            if param == 'now':
                where_str += '(programs.start <= %s AND programs.end >= %s)'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'next':
                where_str += 'programs.start >= %s'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'start':
                where_str += '((programs.start >= %s) OR (programs.start <= %s and programs.end >= %s))'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'end':
                where_str += 'programs.start <= %s'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif len(http_req_args[param]) > 1:
                where_str += 'programs.%s in (' % (param)
                where_str += '%s,' * len(http_req_args[param])
                for i in range(0, len(http_req_args[param])):
                    server_helper.append_value(param, i, db_req_args)
                where_str = where_str[:-1]
                where_str += ')'
            else:
                where_str += 'programs.%s = %%s' % (param)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
    if where_str != '':
        return 'WHERE ' + where_str
    return ''

def make_paging_str(http_req_args, db_req_args):
    paging_str = ''
    if not http_req_args.has_key('limit') and not http_req_args.has_key('count'):
        paging_str = 'LIMIT %d' % server_helper.limit_default
    for arg in server_helper.paging_params:
        if http_req_args.has_key(arg):
            paging_str += '%s %%s ' % arg.upper()
            server_helper.append_value(http_req_args, arg, 0, db_req_args)
    return paging_str

def query_db(db, http_req_args):
    select_target = 'programs.*'
    if http_req_args.has_key('count'):
        select_target = 'COUNT(*) as COUNT'

    db_req_args = []
    where_str = make_where_str(http_req_args, db_req_args)
    paging_str = make_paging_str(http_req_args, db_req_args)

    db_req = 'SELECT %s FROM programs %s ORDER BY programs.start %s;' % (select_target, where_str, paging_str)
    if not server_helper.profile:
        return db.execute(db_req, *db_req_args)
    else:
        ts1 = server_helper.get_ts()
        rows = db.execute(db_req, *db_req_args)
        ts2 = server_helper.get_ts()
        print db_req % tuple(db_req_args)
        print 'Took %f ms' % ((ts2 - ts1) * 1000)
        return rows
