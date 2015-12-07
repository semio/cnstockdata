# -*- coding: utf-8 -*-

# Scrapy settings for cnstockdata project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'cnstockdata'

SPIDER_MODULES = ['cnstockdata.spiders']
NEWSPIDER_MODULE = 'cnstockdata.spiders'
FEED_FORMAT = 'csv'

ITEM_PIPELINES = {
    'cnstockdata.pipelines.FinancialDataPipeline': 300,
    'cnstockdata.pipelines.RecentDataPipeline': 400
    }

DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 10
DOWNLOAD_TIMEOUT = 10

LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'cnstockdata (+https://github.com/semio/cnstockdata)'
