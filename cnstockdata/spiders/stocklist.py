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
from . general import StockDataSpider


class StockListSpider(scrapy.Spider):
    """download full stock list from eastmoney
    """
    name = 'stocklist'
    start_urls = ['http://quote.eastmoney.com/stocklist.html']

    def parse(self, response):
        #TODO: check if the stock had delisted.
        fulllist = response.xpath('//div[@id="quotesearch"]/ul/li/a/text()').extract()
        items = []

        for item in fulllist:
            match = re.match(r'(.*)\((\d+)\)', item)
            name, code = match.groups()
            stockcode = StockCode(name=name, code=code)
            items.append(stockcode)

        return items


class StockSectorSpider(StockDataSpider):
    """download sectors related to stock/stocklist
    """
    name = 'stocksectors'

    def __init__(self, stock=None, *args, **kwargs):

        url_template = \
            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpOtherInfo/stockid/%s/menu_num/2.phtml"

        super(StockSectorSpider, self).__init__(stock, url_template, *args, **kwargs)

    def parse(self, response):
        sectortable = response.xpath('//table[@class="comInfo1"][1]/tr/td/text()').extract()
        assert len(sectortable) == 3

        sector = sectortable[1]

        conceptalbe = response.xpath('//table[@class="comInfo1"][2]/tr/td/text()').extract()

        if conceptalbe[1] == u"对不起，暂时没有相关概念板块信息":
            concepts = ""
        else:
            concepts = ','.join(conceptalbe[1:])

        if isinstance(self.stock, list):
            i = self.start_urls.index(response.url)
            code = self.stock[i]
        else:
            code = self.stock

        return StockSectors(code=code, sector=sector, concepts=concepts)
