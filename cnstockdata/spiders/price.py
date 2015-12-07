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


class HistoryPriceSpider(StockDataSpider):
    """download the history price
    """

    name = 'historyprice'

    def __init__(self, stock=None, pages=None, *args, **kwargs):
        url_template = \
            "http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/%s.phtml"

        super(HistoryPriceSpider, self).__init__(stock, url_template, *args, **kwargs)
        #print self.start_urls[0]
        if pages:
            self.pages = int(pages)
        else: self.pages = 0

    def start_requests(self):
        return [scrapy.Request(url, callback=self.get_pages) for url in self.start_urls]

    def get_pages(self, response):
        current_year = response.xpath('//div[@id="con02-4"]/table[1]/tr/td/form/select[1]/option[@selected]/text()')\
                                   .extract()[0]
        current_sea = response.xpath('//div[@id="con02-4"]/table[1]/tr/td/form/select[2]/option[@selected]')\
                              .xpath('@value')\
                              .extract()[0]
        years = response.xpath('//div[@id="con02-4"]/table[1]/tr/td/form/select[1]/option/text()')\
                        .extract()
        if self.pages:
            pg = self.pages
            sea = int(current_sea)
            year = int(current_year)
            if year != datetime.today().year:
                return
            while pg != 0:
                url = response.url + '?year=' + str(year) + '&jidu=' + str(sea)
                pg = pg - 1
                if sea - 1 == 0:
                    year = year - 1
                    sea = 4
                else: sea = sea - 1
                #print url
                yield scrapy.Request(url, callback=self.parse)
        else:
            #years.sort()
            for year in years:
                if int(year) < 1990:
                    continue
                if int(year) == int(current_year):
                    lsea = int(current_sea)
                else:
                    lsea = 4
                for i in range(lsea, 0, -1):
                    url = response.url + '?year=' + year + '&jidu=' + str(i)
                    yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        rows = response.xpath('//table[@id="FundHoldSharesTable"]/tr')
        items = []

        if len(rows) == 1: # return nothing when no data found
            return

        if isinstance(self.stock, list):
            code = re.match(r'.*(\d{6})', response.url).groups()[0]
        else:
            code = self.stock

        for row in rows[1:]:
            numbers = row.xpath('td/div/text()').extract()

            if len(numbers) == 8:  # older pages contains all data we need with one xpath
                date = numbers[0].strip()
                openp,highp,closep,lowp,volume,yuanvolume,pmultiplier = numbers[1:]
            else: # newer pages we have to extract the date with another xpath
                datetd = row.xpath('td/div/*/text()').extract()
                date = datetd[0].strip()
                openp,highp,closep,lowp,volume,yuanvolume,pmultiplier = numbers[2:]

            item = DailyPrices(code=code,
                               date=date,
                               openp=openp,
                               highp=highp,
                               closep=closep,
                               lowp=lowp,
                               volume=volume,
                               yuanvolume=yuanvolume,
                               pmultiplier=pmultiplier)
            items.append(item)

        return items

class IndexHistorySpider(StockDataSpider):
    """download the history price of index
    """

    name = 'indexhistory'

    def __init__(self, stock=None, *args, **kwargs):
        url_template = \
            "http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s/type/S.phtml"

        super(IndexHistorySpider, self).__init__(stock, url_template, *args, **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            return [scrapy.Request(url, callback=self.get_pages)]

    def get_pages(self, response):
        years = response.xpath('//div[@id="con02-4"]/table[1]/tr/td/form/select[1]/option/text()')\
                        .extract()
        #years.sort()
        for year in years:
            if int(year) < 1990:
                continue
            if int(year) == datetime.today().year:
                lsea = {0:1,
                        1:2,
                        2:3,
                        3:4}.get(datetime.today().month/4)
            else:
                lsea = 4
            for i in range(lsea, 0, -1):
                url = response.url + '?year=' + year + '&jidu=' + str(i)
                yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        #self.logger.info('crawling page %s' %response.url)
        rows = response.xpath('//table[@id="FundHoldSharesTable"]/tr')
        items = []

        if len(rows) == 1: # return nothing when no data found
            return

        if isinstance(self.stock, list):
            code = re.match(r'.*(\d{6})', response.url).groups()[0]
        else:
            code = self.stock

        for row in rows[1:]:
            numbers = row.xpath('td/div/text()').extract()

            if len(numbers) == 7:  # older pages contains all data we need with one xpath
                date = numbers[0].strip()
                openp,highp,closep,lowp,volume,yuanvolume = numbers[1:]
            else: # newer pages we have to extract the date with another xpath
                datetd = row.xpath('td/div/*/text()').extract()
                date = datetd[0].strip()
                openp,highp,closep,lowp,volume,yuanvolume = numbers[2:]

            item = DailyPrices(code=code,
                               date=date,
                               openp=openp,
                               highp=highp,
                               closep=closep,
                               lowp=lowp,
                               volume=volume,
                               yuanvolume=yuanvolume,
                               pmultiplier=1)
            items.append(item)

        return items

class TickDataSpider(CSVFeedSpider):
    """download tick data for specific day
    """
    pass

# TODO:"http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=8&CATALOGID=1110&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1"

class DividendYieldSpider(StockDataSpider):
    """download devidend and yields for stocks
    """
    pass

    #TODO: http://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/300144.phtml
