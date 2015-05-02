#!/bin/env python

"""
pynt task file
"""

import os
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
def get_financialdata():
    '''download fincial data'''
    if os.path.exists('./data/financial.csv'):
        os.remove('./data/financial.csv')

    cmd = sh.Command('scrapy')
    cmd.crawl("financialdata", "-o", "./data/financial.csv")

@task()
def get_stocksectors():
    '''download stock sectors and concepts'''
    if os.path.exists('./data/sectors.csv'):
        os.remove('./data/sectors.csv')

    cmd = sh.Command('scrapy')
    cmd.crawl('stocksectors', '-o', './data/sectors.csv')


