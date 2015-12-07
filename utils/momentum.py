#-*- coding: utf-8 -*-
'''
计算当下的板块动量

1. 从同花顺导出股票的股本数据，所属行业板块
2. 用tushare下载当下所有股票报价
3. 计算板块的加权涨幅，用流通股占比做为权重
'''

import pandas as pd
import numpy as np
import tushare as ts
from datetime import datetime

# 读入同花顺数据
ths = pd.read_csv('./ths.csv', encoding='GB18030', na_values='--')
ths['date'] = datetime.today().date()
ths['code'] = ths[u'代码'].apply(lambda x: x[2:])
ths = ths[[ u'所属行业', u'流通股本',  u'code',  u'date']]
ths.columns = ['industry', 'outstanding', 'code', 'date']

# 下载当前行情
qs = ts.get_today_all()
qs = qs.set_index('code')

# 计算板块动量
res = {}

for ind in ths['industry'].unique():
    df = ths[ths['industry'] == ind].copy()
    df['weight'] = df.outstanding / df.outstanding.sum()
    df = df.set_index('code')
    
    res[ind] = (df['weight'] * qs.ix[df.index][u'changepercent']).sum()
    
res = pd.DataFrame(res, index=['moment'])
mo = res.T.sort_values(by='moment')

# end
print "\n"

print mo.head(5)

print "\n---\n"

print mo.tail(5)