#!/bin/env python

"""
pynt task file
"""

import os
from pynt import task
import sh
from datetime import datetime

@task()
def cleanup():
    '''cleanup all downloaded file'''
    pass

@task()
def get_stocklist():
    '''download the full stock list'''
    if os.path.exists('./data/stocklist.csv'):
        os.remove('./data/stocklist.csv')
    cmd = sh.Command("scrapy")
    cmd.crawl("stocklist", "-o", "./data/stocklist.csv")

#@task('get_stocklist')
@task()
def get_stocklist_mongo():
    '''save the downloaded stocklist to mongodb'''
    from pymongo import MongoClient
    from pandas import read_csv

    client = MongoClient()
    db = client.stock
    stocklist = read_csv('./data/stocklist.csv', dtype={'code': str})
    stocklist = stocklist.set_index('code')

    for idx, name in stocklist.iterrows():
        db.basicinfo.update(
            {'_id': idx},
            {
                '$set': {'name': name[0]}
            },
            upsert=True
        )


@task()
def get_financialdata():
    '''download fincial data'''
    if os.path.exists('./data/financial.csv'):
        os.remove('./data/financial.csv')

    cmd = sh.Command('scrapy')
    cmd.crawl("financialdata", "-o", "./data/financial.csv")

@task()
def get_stocksectors():
    '''download stock sectors and concepts'''
    if os.path.exists('./data/sectors.csv'):
        os.remove('./data/sectors.csv')

    cmd = sh.Command('scrapy')
    cmd.crawl('stocksectors', '-o', './data/sectors.csv')

@task()
def get_prices():
    '''download stock daily prices'''
    from pandas import read_csv

    stocklist = read_csv('./data/stocklist.csv', dtype={'code':str})
    downloadstocks = [i for i in stocklist['code'] if i.startswith(('0', '3', '6'))]

    cmd = sh.Command('scrapy')
    for stock in downloadstocks:
        if os.path.exists('./data/prices/%s.csv' %stock):
            continue
        else:
            name = stocklist[stocklist['code'] == stock].name.iloc[0]
            print '[%s]: start downloading stock %s %s' %(datetime.today(), name, stock)
            cmd.crawl('historyprice', '-a', 'stock=%s' %stock, '-o', './data/prices/%s.csv' %stock)
            print '[%s]: done downloading stock %s %s' %(datetime.today(), name, stock)

@task()
def get_prices_mongo():
    '''save downloaded prices data into mongo db'''
    pass
