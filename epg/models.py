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
from django.db import models

#
# The models defined in this package 
# are not supposed to be modified from any other part of application
# as EPG server is running on it's own database 
# and is designed to work without other apps
# 
class EpgCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    ctg_id = models.IntegerField(db_index=True)
    pr_id = models.IntegerField()
    start = models.IntegerField(db_index=True)
    end = models.IntegerField(db_index=True)
    class Meta:
		db_table = u'categories'
		unique_together = (u'ctg_id', u'pr_id')


class EpgProgram(models.Model):
    pr_id = models.IntegerField(primary_key=True)
    start = models.IntegerField(db_index=True, null=False)
    end = models.IntegerField(db_index=True, null=False)
    aux_id = models.CharField(max_length=384, null=False, db_index=True)
    cat_id = models.IntegerField(null=False)
    rating = models.IntegerField(null=False)
    title = models.TextField(null=False)
    title_l = models.CharField(max_length=48, null=False)
    descr = models.TextField(null=False)
    icon = models.TextField(null=False)
    descr_l = models.CharField(max_length=48, null=False)
    class Meta:
		db_table = u'programs'
		unique_together = ('aux_id', 'start')
