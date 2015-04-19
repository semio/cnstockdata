# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from cnstockdata.items import FinancialData

class FinancialDataPipelie(object):

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
        if isinstance(item, FinancialData):
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


