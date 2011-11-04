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
from django.db import models, connections
from django.db.models import signals
from django.conf import settings
#
# The models defined in this package 
# are not supposed to be modified from any other part of application
# as EPG server is running on it's own database 
# and is designed to work without other apps
# 
class EpgCategory(models.Model):
    id = models.AutoField(primary_key=True)
    ctg_id = models.PositiveIntegerField(db_index=True)
    pr_id = models.PositiveIntegerField()
    start = models.PositiveIntegerField(db_index=True)
    end = models.PositiveIntegerField(db_index=True)
    _index_together = (('ctg_id', 'pr_id'), ('ctg_id','start'))
    class Meta:
		db_table = u'categories'
		unique_together = (u'ctg_id', u'pr_id')


class EpgProgram(models.Model):
    pr_id = models.AutoField(primary_key=True)
    start = models.PositiveIntegerField(db_index=True, null=False)
    end = models.PositiveIntegerField(db_index=True, null=False)
    aux_id = models.CharField(max_length=128, null=False, db_index=True)
    cat_id = models.PositiveIntegerField(null=False)
    rating = models.PositiveIntegerField(null=False)
    title = models.TextField(null=False)
    title_l = models.CharField(max_length=16, null=False)
    descr = models.TextField(null=False)
    icon = models.TextField(null=False)
    descr_l = models.CharField(max_length=16, null=False)
    _index_together = (('aux_id','start'),)
    class Meta:
		db_table = u'programs'
		unique_together = ('aux_id', 'start')



def create_index(model):
    meta = getattr(model, '_meta', None)
    if not meta: return 0
    
    func = create_index_mysql
    
    successes = 0
    index_tuples = getattr(model, '_index_together', [])
    for index_tuple in index_tuples:
        columns = [meta.get_field(field).column for field in index_tuple]
        name = '_'.join(columns)[:63]
        table = meta.db_table
        successes += func(name, table, columns)
        
    if successes:
        print '%d indices created' % successes
    return successes


def create_index_mysql(name, table, columns):
    cursor = connections['epg'].cursor()    
    sql = "CREATE INDEX %s ON %s (%s)" % (
        name, table, ', '.join(columns))
    print sql    
    from MySQLdb import OperationalError
    try:
        cursor.execute(sql)
        return 1
    except OperationalError as x:
        if x.args[0] != 1061: # 1061 means duplicate key name / we can ignore
            raise
        return 0
    finally:
        cursor.close()

def create_all_indices(sender, *args, **kwds):
    model_list = models.get_models(sender)
    for model in model_list:
        create_index(model)


signals.post_syncdb.connect(create_all_indices)
