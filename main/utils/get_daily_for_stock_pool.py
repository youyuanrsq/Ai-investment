#!/usr/bin/env python
# coding: utf-8


import glob
import yfinance as yf
import csv
import datetime
import pandas as pd
import os
import json
from get_dataset import get_single_dataset

# In[4]:

fund_key = ['priceToBook', 'floatShares', 'trailingPE', 'shortPercentOfFloat', 'shortRatio']


def get_data(stock_name='AAPL', start='2010-01-01', end='2015-12-25', interval='1m'):
    df = yf.download(stock_name, start=start, end=end, group_by='ticker', interval=interval, auto_adjust=True)
    return df


end = datetime.date.today()
start = end - datetime.timedelta(days=0)
all_stock_day = []
add_fundamental = 1
dataset = 'ark'
for symbol in get_single_dataset(dataset):
    day_data = get_data(stock_name=symbol, start=start, end=end, interval='1d')
    day_data['symbol'] = symbol
    if add_fundamental:
        funda = yf.Ticker(symbol)
        for key in fund_key:
            try:
                day_data[key] = funda.info[key]
            except:
                day_data[key] = None
    all_stock_day.append(day_data)
all_stock_day = pd.concat(all_stock_day)
all_stock_day.to_csv('../../../trading_data/' + str(end) + '_'+dataset+'_daily_stock.csv')
