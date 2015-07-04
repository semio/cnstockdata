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


class StockDataSpider(scrapy.Spider):
    """This is a abstract class which will download stock related data,
       The class' init method will accept a stock or stock list to start crwaling.
    """
    __metaclass__ = ABCMeta

    def __init__(self, stock=None, url_template=None, *args, **kwargs):
        super(StockDataSpider, self).__init__(*args, **kwargs)

        self.start_urls = []

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

    @abstractmethod
    def parse(self, response):
        pass


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


class HistoryPriceSpider(StockDataSpider):
    """download the history price
    """

    name = 'historyprice'

    def __init__(self, stock=None, pages=0, *args, **kwargs):
        url_template = \
            "http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/%s.phtml"

        super(HistoryPriceSpider, self).__init__(stock, url_template, *args, **kwargs)
        if pages:
            self.pages = int(pages)

    def start_requests(self):
        for url in self.start_urls:
            return [scrapy.Request(url, callback=self.get_pages)]

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
            while pg != 0:
                url = response.url + '?year=' + str(year) + '&jidu=' + str(sea)
                pg = pg - 1
                if sea - 1 == 0:
                    year = year - 1
                    sea = 4
                else: sea = sea - 1
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
