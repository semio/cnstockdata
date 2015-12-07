# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#TODO: add support for mangodb

import re
from pandas import to_datetime
from datetime import datetime
from scrapy.exceptions import DropItem

#from cnstockdata.items import FinancialData

class FinancialDataPipeline(object):

    flist = ['asset_per_share',
             'earning_per_share',
             'cash_per_share',
             'fund_per_share',
             'fixed_assets',
             'luquic_assets',
             'total_assets',
             'long_term_liabilities',
             'incomes',
             'fees',
             'net_profit']

    def process_item(self, item, spider):
        #if isinstance(item, FinancialData):
        if spider.name == 'financialdata':
            for field in self.flist:
                if item.has_key(field):
                    item[field] = inspect_value(item[field])

        return item

def inspect_value(s):
    if u'万' in s:
        strval = re.match(u'(.*)万元', s).groups()[0]
        return float(strval) * 10000
    elif u'元' in s:
        strval = re.match(u'(.*)元', s).groups()[0]
        return float(strval)
    elif s == u'\xa0':
        return 0
    else:
        return float(s)


class RecentDataPipeline(object):
    '''only return data for recent'''

    def process_item(self, item, spider):
        if spider.name == 'historyprice':
            if spider.pages:
                td = to_datetime(datetime.today())
                id = to_datetime(item['date'])
                days = (td - id).days

                if not (days > spider.pages * 100):
                    return item
                # drop the item if the item date is too far from today
                else:
                    raise DropItem('Date too old')

        else:
            return item
