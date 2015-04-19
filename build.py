#!/bin/env python

"""
pynt task file
"""

import sys, os
from pynt import task
import sh

@task()
def cleanup():
    '''cleanup all downloaded file'''
    pass

@task()
def get_stocklist():
    '''download the full stock list'''
    if os.path.exists('./data/stocklist.csv'):
        os.remove('./data/stocklist.csv')
    cmd = sh.Command("scrapy")
    cmd.crawl("stocklist", "-o", "./data/stocklist.csv")

@task()
def get_fincialdata():
    '''download fincial data'''
    import pandas as pd

    from cnstockdata.items import FinancialData
    from cnstockdata.spiders.dataspiders import FinancialDataSpider

    stocklist = pd.read_csv('./data/stocklist.csv')

    
