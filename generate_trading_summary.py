#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os.path
import numpy as np
import glob
import pandas as pd
import datetime
import json
from datetime import date
import yfinance as yf
import csv


# In[26]:


class trade_daily_summary:
    
      
    def __init__(self, path):
        
        self.data, self.trade_time = self.preprocess(path)
        self.open_p = self.get_current_position()
        self.close = self.data['close']
        self.open = self.data['open']
        self.pre_close = self.data['pre_close']
        self.pre_open = self.data['pre_open']

    def get_current_position(self):
        direction =  self.data[self.trade_time[0][1]]['Direction'] 
        position = self.data[self.trade_time[0][1]]['Position']
        if direction == 'buy':
                open_postion = position -1
        elif  direction == 'sell':
                open_postion = position +1
        return open_postion

    def preprocess(self, path):
        extra_keys = ['open','close','pre_open','pre_close']
        stock_path = path
        stock = stock_path.split('/')[-1].split('.')[0]
        with open(stock_path) as f:       
             data = json.load(f)
        time_key = [[change_time_to_number(time), time] for time in list(data.keys()) if time not in extra_keys]
        trade_time = sorted(time_key , key = lambda x : x[0])
        return data , trade_time


    def return_stock_summary(self):

        total_buy = self.open_p * self.pre_close
        stock_change_ratio = ( self.close -  self.pre_close) * 100 / self.pre_close
        buy_size = self.open_p 
        total_sell = 0 
        sell_size = 0
        stock_info = {} 
        for i in self.trade_time:
            trade_index = i[1]
            if self.data[trade_index]['Direction'] == 'buy':
               total_buy += self.data[trade_index]['Price'] * self.data[trade_index]['Size']
               buy_size += self.data[trade_index]['Size']
            elif self.data[trade_index]['Direction'] == 'sell':
               total_sell += self.data[trade_index]['Price'] * self.data[trade_index]['Size']
               sell_size += self.data[trade_index]['Size']
        symbol = self.data[trade_index]['Symbol']
        stock_info[symbol] = {'position': 0, 'day pnl': 0 , 'day pnl ratio':0 ,'pnl':0}
        if buy_size >= sell_size:
            close_size = buy_size - sell_size
            close_sell = close_size * self.close
            total_sell += close_sell     
            final_earning = total_sell - total_buy
            if close_size > 0:
               basic_earning_ratio = final_earning * 100 / (close_size * self.pre_close)
            else:
               basic_earning_ratio = final_earning * 100 / (self.open_p * self.pre_close) 
            stock_info[symbol]['position'] = close_size
            stock_info[symbol]['day pnl'] = round(final_earning, 2)
            stock_info[symbol]['day pnl ratio'] = round(basic_earning_ratio, 2)
        if buy_size < sell_size:
            print('something wrong with position')
        return stock_info
    
    

    
def change_time_to_number(time):
    # time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame({'time': [pd.to_datetime(time)]})
    df_unix_sec = pd.to_numeric(df['time']) [0]
    return df_unix_sec

    
def get_untrade_info(all_log_file, date = "2021-05-22" ):
    all_log = pd.read_csv(all_log_file)
    all_info = {}
    trade_stock = [i.split('/')[-1].split('.')[0] for i in glob.glob(log_save_path+'*.json')]
    all_stock =  [i.split('-')[0] for i in all_log['symbol']]
    untrade_stock  = [i for i in all_stock if i not in trade_stock]
    

    for i in all_log.index:
       symbol = all_log['symbol'][i].split('-')[0]
       data, pre_close, today_close = get_stock_info(symbol, date =  date)
       volume = all_log['volume'][i] 
       if volume > 0:
          pnl_ratio = (today_close - pre_close) * 100 / pre_close
       else:
          pnl_ratio = -(today_close - pre_close) * 100 / pre_close
       pnl = volume * (today_close - pre_close)
       all_info[symbol] = {'position':all_log['volume'][i],'day pnl': pnl, 'day pnl ratio': pnl_ratio, 
                           'pnl': all_log['pnl'][i]}
    
    return all_info

def trade_summary(all_log_file, log_path, date):
    all_log = pd.read_csv(all_log_file)
    trading_info = {}
    for path in glob.glob(log_path + '*.json'):
        trading_info.update(trade_daily_summary(path).return_stock_summary())
    all_trade_info = get_untrade_info(all_log_file, date = date)
    for key in trading_info.keys():
        trading_info[key]['pnl'] = all_trade_info[key]['pnl']
    all_trade_info.update(trading_info)
    return all_trade_info


def get_stock_info(symbol, date = "2021-05-22"  ): 
    today = datetime.datetime.strptime(date,'%Y-%m-%d')
    pre_day = today - datetime.timedelta(days=1)

    data = yf.download(symbol, start= pre_day, end=today)
   # print(data)
    today = today - datetime.timedelta(days=1)
    pre_day = pre_day - datetime.timedelta(days=1)
    pre_day = str(pre_day).split(' ')[0]
    today = str(today).split(' ')[0]
    pre_close = data['Close'][pre_day]
    today_close = data['Close'][today]
    
    return data, pre_close, today_close

def write_summary(log_save_path ,date):
    trade_log  = trade_summary(all_log_file, log_save_path, date)
    f = csv.writer(open(log_save_path + date+"_trading_summary.csv", "w+"))
    f.writerow(["symbol","position", "day pnl", "day pnl ratio", "total pnl"])
    for x in trade_log.keys():
        y = trade_log[x]
        #print(y['position'], y['day pnl'], y['day pnl ratio'], y['pnl'])
        f.writerow([x, y['position'], y['day pnl'], y['day pnl ratio'], y['pnl']])
    print('the trading summary is saved in ', log_save_path + date+"_trading_summary.csv")
    


# In[ ]:


'''
args:
    log save_path: where you store all your daily trading json file
    all_log_file : the location of all_postion.csv from IB
output:
    a simple csv with daily trading pnl and total pnl 

'''


# In[27]:


log_save_path = '/home/zhubo/Documents/fda_check/test2/comparie/'
all_log_file = log_save_path + 'all_position.csv'
date = '2021-05-21'
write_summary(log_save_path, date)
           

