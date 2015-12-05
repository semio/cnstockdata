# -*- coding: utf-8 -*-
"""
Data Spiders.
"""
from abc import ABCMeta, abstractmethod
from cnstockdata.items import *
from scrapy.contrib.spiders import CSVFeedSpider
import scrapy
import re
import logging
from datetime import datetime
from .general import StockDataSpider


class FinancialDataSpider(StockDataSpider):
    """download financial data from sina finance.
    """
    name = 'financialdata'

    def __init__(self, stock=None, *args, **kwargs):

        url_template = \
            "http://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/%s/displaytype/4.phtml"

        super(FinancialDataSpider, self).__init__(stock, url_template, *args, **kwargs)

    def parse(self, response):

        numbers = response.xpath('//table[@id="FundHoldSharesTable"]/tr')\
                  .xpath('td[@class="tdr"]//text()').extract()
        l = len(numbers)
        groups = [numbers[i:i+l/4] for i in range(0, l, l/4)]
        items = []

        if isinstance(self.stock, list):
            code = re.match(r'.*(\d{6})', response.url).groups()[0]
        else:
            code = self.stock

        for g in groups:

            date,\
            asset_per_share,\
            earning_per_share,\
            cash_per_share,\
            fund_per_share,\
            fixed_assets,\
            luquic_assets,\
            total_assets,\
            long_term_liabilities,\
            incomes,\
            fees,\
            net_profit = g[1:]

            item = FinancialData(code=code,
                                 date=date,
                                 asset_per_share=asset_per_share,
                                 earning_per_share=earning_per_share,
                                 cash_per_share=cash_per_share,
                                 fund_per_share=fund_per_share,
                                 fixed_assets=fixed_assets,
                                 luquic_assets=luquic_assets,
                                 total_assets=total_assets,
                                 long_term_liabilities=long_term_liabilities,
                                 incomes=incomes,
                                 fees=fees,
                                 net_profit=net_profit)
            items.append(item)

        return items

class FinancialDataSpider2(scrapy.Spider):
    """financial data spider, may replace the above one"""

    name = 'financialdata2'

    def __init__(self, stock=None, url_template=None, type=None, *args, **kwargs):
        super(StockDataSpider, self).__init__(*args, **kwargs)

        self.start_urls = []
        self.url_templates = [
            #TODO: fix this
        ]

        if stock:
            self.stock = stock
            self.start_urls = [url_template %stock]
        else:
            self.stock = []
            import csv
            with open('./data/stocklist.csv', 'rb') as f: #TODO: add option to choose file
                csvstr = csv.reader(f, delimiter=',')
                for row in csvstr:
                    if re.match(r'^[036]\d+', row[0]):
                        self.start_urls.append(url_template %row[0])
                        self.stock.append(row[0])

    def parse(self, response):
        pass
