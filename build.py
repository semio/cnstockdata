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
def get_fincialdata():
    '''download fincial data'''
    if os.path.exists('./data/fincial.csv'):
        os.remove('./data/fincial.csv')

    cmd = sh.Command('scrapy')
    cmd.crawl("fincialdata", "-o", "./data/fincial.csv")

