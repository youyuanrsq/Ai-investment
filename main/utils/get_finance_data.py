import glob
import yfinance as yf
import csv

import datetime
import pandas as pd
import os
for get
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json


def get_data(stock_name='AAPL', start='2010-01-01', end='2015-12-25', interval='1m'):
    stock_names = stock_name.split()
    df = yf.download(stock_name, start=start, end=end, group_by='ticker', interval=interval, auto_adjust=True)
    return df


def get_stock_price_info(ticker, period='1y', interval='1d', ):
    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers=ticker,

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period=period,

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval=interval,

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by='ticker',

        # adjust all k line automatically
        # (optional, default is False)
        auto_adjust=True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost=False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads=True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy=None
    )
    return data



if __name__ == "__main__":

    dataset = 'top5000'
    intraday_data_type = []  # ['1min','15min','45min','60min']
    day_data_type = ['day']  # ,'week','month']
    save_data = '../../../trading_data'

    if not os.path.isdir(save_data):
        print('new directry has been created')
        os.mkdir(save_data)
    if not os.path.isdir(save_data + '/' + dataset):
        print('new directry has been created')
        os.mkdir(save_data + '/' + dataset)
    for i in intraday_data_type + day_data_type:
        if not os.path.isdir(save_data + '/' + dataset + '/' + i):
            print('new directry has been created')
            os.mkdir(save_data + '/' + dataset+ '/' + i)


    if 'day' in day_data_type:
        intraday = []
        for symbol in download_dataset:
            try:
                print(symbol)
                data = pd.read_csv(
                    'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + symbol + '&outputsize=full&apikey=H40LS6V3016EZSQ6&datatype=csv')
                data.to_csv(save_data + '/' + dataset + '/' + 'day' + '/' + symbol + '.CSV')
            except Exception as e:
                print(e)

    if 'week' in day_data_type:
        intraday = []
        for symbol in download_dataset:
            try:
                print(symbol)
                data = pd.read_csv(
                    'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=' + symbol + '&outputsize=full&apikey=H40LS6V3016EZSQ6&datatype=csv')
                data.to_csv(save_data + '/' + dataset + '/' + 'week' + '/' + symbol + '.CSV')
            except Exception as e:
                print(e)
    if len(intraday_data_type) > 0:
        intraday = []
        for symbol in download_dataset:
            for interval in intraday_data_type:
                print(symbol)
                try:
                    for z in range(1, 3):
                        for x in range(1, 13):
                            time = 'year' + str(z) + 'month' + str(x)
                            print(time)
                            data = pd.read_csv(
                                'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=' + symbol + '&interval=' + interval + '&slice=' + time + '&apikey=H40LS6V3016EZSQ6')
                            data.to_csv(save_data + '/' + dataset + '/' + interval + '/' + symbol + '.CSV')
                except Exception as e:
                    print(e)
    if len(intraday_data_type) > 0:
        for symbol in download_dataset:
            for interval in intraday_data_type:
                print(symbol)
                try:
                    all_data = []
                    bad_data = 0
                    for z in range(1, 3):
                        for x in range(1, 13):
                            try:
                                time = 'year' + str(z) + 'month' + str(x)
                                print(time)
                                df = pd.read_csv(save_data + '/' + dataset + '/' + interval + '/' + symbol + '.CSV')
                                df['time'] = pd.to_datetime(df['time'])
                                all_data.append(df)
                            except Exception as e:
                                print(e)

                    all_data = pd.concat(all_data)
                    if bad_data == 0:
                        intrady_data = []
                        for year in [2021, 2020, 2019]:
                            for month in range(12, 0, -1):
                                for day in range(31, 0, -1):
                                    if month in [11, 12, 1, 2] or (month in [3] and day < 15):
                                        td_start, td_close = '10:28:00', '17:01:00'
                                    else:
                                        td_start, td_close = '09:28:00', '16:01:00'
                                    date_start = str(year) + '-' + str(month) + '-' + str(day) + ' ' + td_start
                                    date_close = str(year) + '-' + str(month) + '-' + str(day) + ' ' + td_close

                                    try:
                                        date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
                                        date_close = datetime.datetime.strptime(date_close, '%Y-%m-%d %H:%M:%S')

                                        intrady_data.append(
                                            all_data[(all_data['time'] > date_start) & (all_data['time'] < date_close)])
                                    except Exception as e:
                                        print(e)

                                    final_data = pd.concat(intrady_data)
                                    final_data.to_csv(
                                        save_data + '/' + dataset + '/' + interval + '/' + symbol + '_' + interval + '.CSV')
                except Exception as e:
                    print(e)
        os.system("rm ../../../trading_data/" + dataset + "/*/*month*")
        os.system("zip -r " + dataset + " ../../../trading_data/" + dataset)
