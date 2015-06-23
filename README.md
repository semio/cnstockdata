中国股票数据下载器，使用网上免费的数据源如东方财富网，新浪财经等。

看过下载回来的数据，发现这些免费数据有些不完整的地方（特别是财务数据），如果对数据质量有要求的还是选择一些付费的服务更好（如[预测者](http://yucezhe.com/product?name=financial-data)）

## Depandency

* scrapy

## 目前已经实现的功能

下载所有股票列表（含已退市股票）：

```scrapy crawl stocklist -o ./data/stocklist.csv```

下载某个股票的最近几次季报的财务数据摘要：

```scrapy crawl financialdata -a stock=000001 -o ./data/000001.csv```

所有股票的财务数据摘要（将从```data/stocklist.csv```读取股票列表）：

```scrapy crawl financialdata -o ./data/financial.csv```

下载某个股票的所属行业和概念：

```scrapy crawl stocksectors -a stock=000001 -o ./data/sec000001.csv```

所有股票的所属行业和概念：

```scrapy crawl stocksectors -o ./data/secetors.csv```
