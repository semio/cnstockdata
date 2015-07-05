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
def get_prices_updates():
    '''download stock daily prices for last 2 seasons'''
    from pandas import read_csv

    stocklist = read_csv('./data/stocklist.csv', dtype={'code':str})
    downloadstocks = [i for i in stocklist['code'] if i.startswith(('0', '3', '6'))]

    cmd = sh.Command('scrapy')
    for stock in downloadstocks:
        if os.path.exists('./data/prices/updates/%s.csv' %stock):
            continue
        else:
            name = stocklist[stocklist['code'] == stock].name.iloc[0]
            print '[%s]: start downloading stock %s %s' %(datetime.today(), name, stock)
            cmd.crawl('historyprice', '-a', 'stock=%s' %stock, '-a', 'pages=2', '-o', './data/prices/updates/%s.csv' %stock)
            print '[%s]: done downloading stock %s %s' %(datetime.today(), name, stock)

@task()
def get_prices_mongo():
    '''insert all downloaded prices into mongodb'''
    import pandas as pd
    from pymongo import MongoClient

    stocklist = pd.read_csv('./data/stocklist.csv', dtype={'code':str})
    downloadstocks = [i for i in stocklist['code'] if i.startswith(('0', '3', '6'))]
    client = MongoClient()
    db = client.stock

    for i, stock in enumerate(downloadstocks):
        if i % 100 == 0:
            print 'done %d stocks' %i

        try:
            data1 = pd.read_csv('./data/prices/%s.csv' %stock)
        except:
            data1 = pd.DataFrame([])

        try:
            data2 = pd.read_csv('./data/prices/updates/%s.csv' %stock)
        except:
            data2 = pd.DataFrame([])

        if data1.empty and data2.empty:
            print 'no data for %s' %stock
            continue
        else:
            df = pd.concat([data1, data2]).drop_duplicates()
            df.date = pd.to_datetime(df.date)
            df.sort_index(by='date', inplace=True)
            items = df.to_dict('record')
            for i in items:
                i.update({'basicinfo_id': stock})
            db.historyprice.insert_many(items)



