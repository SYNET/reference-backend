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

import sys
import xmltv

cat_id = 1

if sys.hexversion >= 0x2050000:
    from xml.etree.cElementTree import ElementTree, Element, SubElement, tostring
else:
    try:
        from cElementTree import ElementTree, Element, SubElement, tostring
    except ImportError:
        from elementtree.ElementTree import ElementTree, Element, SubElement, tostring

def find_cats(cont):
	res = {}
	for item in cont:
		#if item.has_key('category'):
		#	for category in item['category']:
		#		if not category in res.keys():
		#			res[category] = []
		#		if item.has_key('id'):
		#			res[category].append(item['id'])
		if item.has_key('genre'):
			for category in item['genre']:
				key = (category, 'unknown')
				if not key in res.keys():
					res[key] = []
				if item.has_key('id'):
					res[key].append(item['id'])
	return res

def write_cats(root, cont, is_channel_cats):
	global cat_id
	for item in cont.keys():
		if not item[0]:
			continue
		elem = SubElement(root, 'Category')
		if item[1]:
			elem.set('lang', item[1])
		elem.set('id', str(cat_id))
		cat_id += 1
		if is_channel_cats:
			for ch in cont[item]:
				ch_elem = SubElement(elem, 'Channel')
				ch_elem.set('id', ch)
			elem.set('channel', 'true')
		elem.set('name', item[0])

if len(sys.argv) != 2:
	print 'Usage: %s epg.xml' % sys.argv[0]
	sys.exit(-1)

channel_cats = find_cats(xmltv.read_channels(open(sys.argv[1])))
programmes_cats = find_cats(xmltv.read_programmes(open(sys.argv[1])))

root = Element('Categories')
et = ElementTree(root)
write_cats(root, channel_cats, True)
write_cats(root, programmes_cats, False)
et.write(sys.stdout, 'UTF-8')
