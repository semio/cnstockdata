import scrapy
from cnstockdata.items import StockCode
import re

class StockListSpider(scrapy.Spider):
    name = 'stocklist'
    start_urls = ['http://quote.eastmoney.com/stocklist.html']

    def parse(self, response):
        fulllist = response.xpath('//div[@id="quotesearch"]/ul/li/a/text()').extract()
        for item in fulllist:
            g = re.match(r'(.*)(\(\d+\))', item)
            name, code = g.groups()
            scrapy.log.msg('got item %s' %code)

