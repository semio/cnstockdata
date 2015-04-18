import scrapy
from cnstockdata.items import StockCode
import re

class StockListSpider(scrapy.Spider):
    name = 'stocklist'
    start_urls = ['http://quote.eastmoney.com/stocklist.html']

    def parse(self, response):
        fulllist = response.xpath('//div[@id="quotesearch"]/ul/li/a/text()').extract()
        items = []

        for item in fulllist:
            match = re.match(r'(.*)\((\d+)\)', item)
            name, code = match.groups()
            stockcode = StockCode(name=name, code=code)
            items.append(stockcode)

        return items

class TickDataSpider(scrapy.Spider):
    pass

class FinancialDataSpider(scrapy.Spider):
    pass
