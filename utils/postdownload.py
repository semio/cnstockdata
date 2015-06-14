# coding=utf-8
#!/usr/bin/env python

from pymongo import MongoClient
from datetime import datetime
import os
import pandas as pd
from pandas import read_csv

full_list = read_csv('../data/stocklist.csv', dtype={'code': str})

listedAshare = full_list['code'].map(lambda x: x.startswith(('0', '3', '6')))

stocklist = full_list[listedAshare]

def insert_daily_closes():

    client = MongoClient()
    db = client.stock

    for stock in stocklist.code[:10]:
        fname = '../data/prices/%s.csv' %stock
        if os.path.exists(fname):
            prices = read_csv(fname, dtype={'code': str})
            prices['date'] = pd.to_datetime(prices['date'])
            prices.drop(['code'], axis=1, inplace=True)

            d = []
            m = []
            for r in prices.iterrows():
                m.append(r)

            for i in m:
                d.append({
                    'closep': i[1][0],
                    'date': i[1][6],
                    'pmultiplier': i[1][1],
                    'yuanvol': i[1][2],
                    'high': i[1][3],
                    'vol': i[1][4],
                    'lowp': i[1][5],
                    'openp': i[1][7]
                })




if __name__ == '__main__':
    insert_record()
