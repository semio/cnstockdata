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
