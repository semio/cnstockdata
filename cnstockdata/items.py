# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StockCode(scrapy.Item):
    '''stock code and it's name'''
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    code = scrapy.Field()

class FinancialData(scrapy.Item):
    '''Latest financial data for stocks'''
    code = scrapy.Field()
    date = scrapy.Field()
    # 以下变量分别为
    # 每股净资产, 每股收益, 每股现金含量, 每股资本公积金, 固定资产合计, 流动资产合计, 资产总计,
    # 长期负债合计, 主营业务收入, 财务费用, 净利润
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
    net_profit = [scrapy.Field()] * 11

class FinancialData2(scrapy.Item):
    '''financial data item for singal term, may replace the financial data above'''
    code = scrapy.Field()
    date = scrapy.Field()
    rtype = scrapy.Field()
    season = scrapy.Field()
    value = scrapy.Field()

class StockSectors(scrapy.Item):
    '''stock code and sectors'''
    code = scrapy.Field()
    sector = scrapy.Field()
    concepts = scrapy.Field()

class DailyPrices(scrapy.Item):
    '''daily stock prices'''
    date = scrapy.Field()
    code, openp, highp, closep, lowp = [scrapy.Field()] * 5
    volume, yuanvolume, pmultiplier = [scrapy.Field()] * 3
