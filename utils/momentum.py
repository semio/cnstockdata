#-*- coding: utf-8 -*-
'''
计算当下的板块动量

1. 从同花顺导出股票的股本数据，所属行业板块
2. 用tushare下载当下所有股票报价
3. 计算板块的加权涨幅，用市值占比做为权重
'''

import pandas as pd
import numpy as np
import tushare as ts
from datetime import datetime

# 读入同花顺数据
ths = pd.read_excel('../data/ths.xlsx', encoding='GB18030', na_values='--')
ths['date'] = datetime.today().date()
ths['code'] = ths[u'代码'].apply(lambda x: x[2:])
ths = ths[[ u'所属行业', u'流通市值',  u'code',  u'date']]
ths.columns = ['industry', 'outstanding', 'code', 'date']

# 下载当前行情
qs = ts.get_today_all()
qs = qs.set_index('code')
qs = qs.drop_duplicates()

# 计算板块动量
res = {}

for ind in ths['industry'].unique():
    df = ths[ths['industry'] == ind].copy()
    df = df.set_index('code')
    trade = qs.ix[df.index]['trade']
    val = trade * df.outstanding
    df['weight'] = val / val.sum()

    momt = (df['weight'] * qs.ix[df.index][u'changepercent']).sum()
    turn = (df['weight'] * qs.ix[df.index][u'turnoverratio']).sum()
    res[ind] = {'turnover': turn, 'momentum': momt}


res = pd.DataFrame(res).T
mo1 = res.sort_values(by='momentum').head(5)
mo2 = res.sort_values(by='momentum', ascending=False).head(5)

# end
print "\n"
print mo1
print "\n---\n"
print mo2
