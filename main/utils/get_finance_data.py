import glob
import yfinance as yf
import csv

import datetime
import pandas as pd
import os

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


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


def get_ticker():
    url = ("https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=NYSE&apikey=demo")
    NYSE_company = get_jsonparsed_data(url)
    NYSE_company_info = {}
    for i in NYSE_company:
        NYSE_company_info[i['symbol']] = i
    url = ("https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=NASDAQ&apikey=demo")
    NASDAQ_company = get_jsonparsed_data(url)
    NASDAQ_company_info = {}
    for i in NASDAQ_company:
        NASDAQ_company_info[i['symbol']] = i
    url = ("https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=AMEX&apikey=demo")
    AMEX_company = get_jsonparsed_data(url)
    AEMX_company_info = {}
    for i in AMEX_company:
        AEMX_company_info[i['symbol']] = i
    return NYSE_company_info, NASDAQ_company_info, AEMX_company_info


def read_ark():
    ark_stock = []
    for i in glob.glob('../../test_data/dataset/ark/*csv'):
        ark = pd.read_csv(i)
        for z in ark['ticker']:
            ark_stock.append(z)
    return ark_stock


if __name__ == "__main__":

    dataset = 'nasdaq100'
    intraday_data_type = []  # ['1min','15min','45min','60min']
    day_data_type = ['day']  # ,'week','month']
    save_data = '../../trading_data'

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

    if dataset == 'all':
        all_tickers = []
        NYSE_company, NASDAQ_company, AEMX_company = get_ticker()
        for com in [NASDAQ_company, AEMX_company]:
            for symbol in com.keys():
                all_tickers.append(symbol)
        #        break
        download_dataset = all_tickers
    elif dataset == 'top100':
        download_dataset = pd.read_csv('../../test_data/dataset/top-100-stocks-to-buy-04-06-2021.csv')['Symbol']
    elif dataset == 'sp500':
        download_dataset = pd.read_csv('../../test_data/dataset/sp500.csv')['Symbol']
    elif dataset == 'ark':
        download_dataset = read_ark()
    elif dataset == 'rusell1000':
        download_dataset = pd.read_csv('../../test_data/dataset/russell-1000-index-05-21-2021.csv')['Symbol']
    elif dataset == 'nasdaq100':
        download_dataset = pd.read_csv('../../test_data/dataset/nasdaq100-05-21.csv')['Symbol']

    print('starting data downloading for ' + dataset)
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
        os.system("rm ../../trading_data/" + dataset + "/*/*month*")
        os.system("zip -r " + dataset + " ../../trading_data/" + dataset)
