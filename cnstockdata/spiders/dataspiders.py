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

        self.start_urls = []
        url_sheme = "http://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/%s/displaytype/4.phtml"

        if stock:
            self.stock = stock
            self.start_urls = [url_sheme %stock]
        else:
            self.stock = []
            import csv
            with open('./data/stocklist.csv', 'rb') as f:
                csvstr = csv.reader(f, delimiter=',')
                for row in csvstr:
                    if re.match(r'^[036]\d+', row[0]):
                        self.start_urls.append(url_sheme %row[0])
                        self.stock.append(row[0])

        if len(self.start_urls) < 1:
            raise ValueError('no url found')


    def parse(self, response):

        numbers = response.xpath('//table[@id="FundHoldSharesTable"]/tr')\
                  .xpath('td[@class="tdr"]//text()').extract()
        l = len(numbers)
        groups = [numbers[i:i+l/4] for i in range(0, l, l/4)]
        items = []

        if isinstance(self.stock, list):
            i = self.start_urls.index(response.url)
            code = self.stock[i]
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
