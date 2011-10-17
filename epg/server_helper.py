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

import time

profile = False

where_params = [
    'start',
    'now',
    'next',
    'end',
    'aux_id',
    'cat_id',
    'rating',
    'title',
    'title_l',
    'descr',
    'descr_l',
    'ctg_id',
]
paging_params = [
    'limit',
    'offset',
]
int_params = [
    'start',
    'now',
    'next',
    'end',
    'cat_id',
    'rating',
    'category',
    'offset',
    'limit',
    'ctg_id',
]
other_params = [
    'count',
]

limit_max = 1000
limit_default = 1000

def append_value(http_req_args, arg_name, arg_idx, arg_list):
    if arg_name in int_params:
        arg_list.append(int(http_req_args[arg_name][arg_idx]))
    else:
        arg_list.append(http_req_args[arg_name][arg_idx])

def get_ts():
    return time.time()
