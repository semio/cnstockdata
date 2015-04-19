import scrapy
from cnstockdata.items import StockCode, FinancialData
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
    name = 'financialdata'

    def __init__(self, stock=None, *args, **kwargs):
        super(FinancialDataSpider, self).__init__(*args, **kwargs)

        self.stock = stock
        self.start_urls = ["http://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/%s/displaytype/4.phtml" \
                           %stock]

    def parse(self, response):
        numbers = response.xpath('//table[@id="FundHoldSharesTable"]/tr')\
                  .xpath('td[@class="tdr"]//text()').extract()
        l = len(numbers)
        scrapy.log.msg('length is %d' %l)
        groups = [numbers[i:i+l/4] for i in range(0, l, l/4)]
        items = []

        for g in groups:
            code = self.stock

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
