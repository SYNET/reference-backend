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

def make_ctg_where_str(http_req_args, db_req_args):
    where_str = ''
    for param in http_req_args.keys():
        if param in server_helper.where_params:
            if where_str != '':
                where_str += ' AND '

            if param == 'now':
                where_str += '(categories.start <= %s AND categories.end >= %s)'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'next':
                where_str += 'categories.start >= %s'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'start':
                where_str += '((categories.start >= %s) OR (categories.start <= %s and categories.end >= %s))'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'end':
                where_str += 'categories.end <= %s'
                server_helper.append_value(http_req_args, param, 0, db_req_args)
            elif param == 'ctg_id':
                # if there're more then one ctg_id
                # then we making compound id = (parent_ctg_id << 16 | ctg_id)
                # first ctg_id is parent id
                if len(http_req_args[param]) > 1:
                    where_str += 'categories.%s = %%s' % (param)
                    db_req_args.append(int(http_req_args[param][0]) << 16 | int(http_req_args[param][1]))
                else:
                    where_str += 'categories.%s = %%s' % (param)
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
    # Get pr_ids for ctg_ids and time
    db_req_args = []
    select_target = 'pr_id'
    if http_req_args.has_key('count'):
        select_target = 'COUNT(*) as COUNT'

    ctg_where_str = make_ctg_where_str(http_req_args, db_req_args)
    paging_str = make_paging_str(http_req_args, db_req_args)
    db_req = 'SELECT %s FROM categories %s ORDER BY categories.start %s' % (select_target, ctg_where_str, paging_str);
    ts1 = server_helper.get_ts()
    db.execute(db_req, db_req_args)
    rows = server_helper.dictfetchall(db)
    ts2 = server_helper.get_ts()
    if server_helper.profile:
        print db_req % tuple(db_req_args)
        print 'categories: Took %f ms' % ((ts2 - ts1) * 1000)

    if (http_req_args.has_key('count')):
        return rows

    pr_ids = [row['pr_id'] for row in rows]

    if len(pr_ids) == 0:
        return []

    prg_where_str = '%s,' * len(pr_ids)
    prg_where_str = prg_where_str[:-1]
    prg_where_str = 'WHERE pr_id in (%s)' % prg_where_str
    
    db_req = 'SELECT * FROM programs %s ORDER BY programs.start;' % (prg_where_str)
    ts1 = server_helper.get_ts()
    db.execute(db_req, pr_ids)
    rows = server_helper.dictfetchall(db)
    ts2 = server_helper.get_ts()
    if server_helper.profile:
        print db_req % tuple(pr_ids)
        print 'programs: Took %f ms' % ((ts2 - ts1) * 1000)
    return rows
