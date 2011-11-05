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

from distutils.core import setup, Extension

module1 = Extension('binwriter', sources = ['binwriter.c'])

setup (name = 'binwriter',
    version = '0.0',
    description = 'SyNET binary writer',
    ext_modules = [module1])
