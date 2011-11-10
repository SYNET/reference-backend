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

from epg import xmltv
from dateutil import parser
import sys
import time, calendar
import codecs
from xml.etree.cElementTree import ElementTree, Element, SubElement, tostring
from django.db import connections
from django.db.models import Max, Count
from django.core.management.base import BaseCommand, CommandError
from epg.models import EpgCategory, EpgProgram

def insert_programs(printout, conn, programs, categories):
    cursor = conn.cursor()
    prog_id = 1
    for p in programs:
        title = title_lang = descr = descr_lang = icon = ''
        cat_id = 0
        rating = 0

        if p.has_key('catalog_id'):
            cat_id = int(p['catalog_id'][0])

        if p.has_key('icon') and p['icon'][0].has_key('src'):
            icon = p['icon'][0]['src']

        aux_id = codecs.utf_8_encode(p['channel'])[0]

        start = int(calendar.timegm(parser.parse(p['start']).utctimetuple()))
        end = int(calendar.timegm(parser.parse(p['stop']).utctimetuple()))

        if p.has_key('title'):
            title = codecs.utf_8_encode(p['title'][0][0])[0]
            title_lang = codecs.utf_8_encode(p['title'][0][1])[0]

        if p.has_key('desc'):
            if p['desc'][0][0]:
                descr = codecs.utf_8_encode(p['desc'][0][0])[0]
            if p['desc'][0][1]:
                descr_lang = codecs.utf_8_encode(p['desc'][0][1])[0]

        if p.has_key('genre'):
            genres = p['genre']
            for g in genres:
                if not g:
                    printout.write(u'*** Empty category in [%s] %s\n' % (p['start'], p['title'][0][0]))
                    continue
                if g not in categories.keys():
                    printout.write('*** Category %s is not known\n' % g.encode('UTF-8'))
                    continue
                if categories[g].has_key('parent'):
                    parents = categories[g]['parent']
                    # if category has only one parent, 
                    # we insert in db pairs: (ctg_id, prog_id), (parent_ctg_id, prog_id)
                    if (len(parents) == 1):
                        cursor.execute('''REPLACE INTO categories(ctg_id, pr_id, start, end)
                            VALUES(%s, %s, %s, %s);''', (categories[parents[0]]['id'], prog_id, start, end))
                        #TODO: remove after moving to new ctg_id scheme
                        cursor.execute('''REPLACE INTO categories(ctg_id, pr_id, start, end)
                            VALUES(%s, %s, %s, %s);''', (categories[g]['id'], prog_id, start, end))
                        if parents[0] not in genres:
                            id = (categories[parents[0]]['id'] << 16) | categories[g]['id']
                            cursor.execute('''REPLACE INTO categories(ctg_id, pr_id, start, end)
                                VALUES(%s, %s, %s, %s);''', (id, prog_id, start, end))

                    # otherwise we insert in db pair (parent_ctg_id << 16 | ctg_id, prog_id)
                    for parent in parents:
                        if parent in genres:
                            id = (categories[parent]['id'] << 16) | categories[g]['id']
                            cursor.execute('''REPLACE INTO categories(ctg_id, pr_id, start, end)
                                VALUES(%s, %s, %s, %s);''', (id, prog_id, start, end))

                else:
                    cursor.execute('''REPLACE INTO categories(ctg_id, pr_id, start, end)
                        VALUES(%s, %s, %s, %s);''', (categories[g]['id'], prog_id, start, end))
        else:
            for c in categories.keys():
                if aux_id in categories[c]['channels']:
                    cursor.execute('''REPLACE INTO categories(ctg_id, pr_id, start, end)
                        VALUES(%s, %s, %s, %s);''', (categories[c]['id'], prog_id, start, end))
	try : 
         cursor.execute('''INSERT INTO programs (pr_id, start, end,
            aux_id, cat_id, rating,
            title, title_l,
            descr, descr_l, icon)
            VALUES (%s, %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s, %s)''',
            (prog_id, start, end, aux_id, cat_id, rating,
            title, title_lang, descr, descr_lang, icon))
         prog_id += 1
        except Exception, e:
         printout.write('*** cant save program aux=%s chan=%s, start=\"%s\", title=\"%s\"\n' % (aux_id, p['channel'], p['start'], p['title'][0][0]))
         printout.write('      error was %s \n' % e) 
    cursor.execute('''CHECK TABLE categories''')
    cursor.execute('''REPAIR TABLE categories''')
    cursor.execute('''CHECK TABLE programs''')
    cursor.execute('''REPAIR TABLE programs''')

    cursor.close()
    conn.commit()

def parse_category(printout, elem, parent, categories):
    retval = {}
    channels = []
    if 'channel' in elem.keys() and elem.get('channel') == 'true':
        for channel in elem.findall('Channel'):
            channels.append(channel.get('id'))
    try:
        retval['id'] = int(elem.get('id'))
    except ValueError:
        printout.write('*** Category ID is not integer!\n')
        sys.exit(-1)

    if retval['id'] < 1 or retval['id'] > 65535:
        printout.write('ID of category %s is out of bounds!\n' % elem.get('name').encode('UTF-8'))
        sys.exit(-1)

    retval['channels'] = channels
    if parent:
        if not 'channel' in parent.keys():
            printout.write('ERROR! only channel category can be top category!\n')
            sys.exit(-1)
        retval['parent'] = [ parent.get('name') ]
    if categories.has_key(elem.get('name')):
        old_cat = categories[elem.get('name')]
        if old_cat['id'] != retval['id']:
            printout.write('ERROR! found categories %s with same name but different id!\n' % elem.get('name').encode('UTF-8'))
            sys.exit(-1)
        if len(old_cat['channels']) != 0 or len(retval['channels']):
            printout.write('ERROR! found duplicate channel categories!\n')
            sys.exit(-1)
        if not retval.has_key('parent') or not old_cat.has_key('parent'):
            printout.write('ERROR! found duplicate categories of different level!\n')
        old_cat['parent'].extend(retval['parent'])
        categories[elem.get('name')] = old_cat
    else:
        categories[elem.get('name')] = retval

    for category in elem.findall('Category'):
        parse_category(printout, category, elem, categories)
    return categories

def parse_categories(printout, fn):
    categories = {}
    et = ElementTree()
    tree = et.parse(fn)
    for elem in tree.findall('Category'):
        parse_category(printout, elem, None, categories)
    return categories

def assign_catalog_ids(printout):
	catID = EpgProgram.objects.aggregate(Max('cat_id'))['cat_id__max']
	for dup in EpgProgram.objects.values('title').annotate(dup_count=Count('title')).filter(dup_count__gt=1):
		catID += 1
		updateCount = EpgProgram.objects.filter(title=dup['title']).update(cat_id=catID)
		printout.write('Assigned catalog id=%d to %d programs named %s\n' % (catID, updateCount, dup['title']))


class Command(BaseCommand):
	args = '<epg program in XMLTV format> <categories list>'
	
	def handle(self, *args, **options):
		self.stdout = codecs.getwriter('utf-8')(self.stdout, errors='replace')
		self.stderr = codecs.getwriter('utf-8')(self.stderr, errors='replace')
				
		if len(args) != 2:
			raise CommandError('importepg <epg program in XMLTV format> <categories list>\n')
		
		conn = connections['epg']
		self.stdout.write('Parsing categories...'); self.stdout.flush()
		try:
			categories = parse_categories(self.stderr, args[1])
		except Exception as e:
			raise CommandError('*** Error while parsing %s: %s' % (args[1], e))
		self.stdout.write('done!\n')

		self.stdout.write('Parsing EPG from %s...' % args[0]); self.stdout.flush()
		try:
			programmes = xmltv.read_programmes(open(args[0], 'r'))
		except Exception as e:
			raise CommandError('*** Error while parsing %s: %s\n' % (args[0], e))
			return
		
		programmes.sort(key = lambda program : int(calendar.timegm(parser.parse(program['start']).utctimetuple())))
		self.stdout.write('done!\n')
		
		self.stdout.write ('Purging old data...'); self.stdout.flush()
		EpgProgram.objects.all().delete()
		EpgCategory.objects.all().delete()
		self.stdout.write('done!\n')
		
		self.stdout.write('Inserting data to DB'); self.stdout.flush()
		insert_programs(self.stderr, conn, programmes, categories)
		self.stdout.write('done!\n')
		
		self.stdout.write("Joining matching programs...\n")
		assign_catalog_ids(self.stderr)
