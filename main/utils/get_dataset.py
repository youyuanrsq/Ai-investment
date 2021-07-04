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
def get_single_dataset(dataset):
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
    elif dataset == 'top5000':
        download_dataset = pd.read_csv('../../test_data/dataset/earnings_calendar.csv')['symbol']
    print('starting data downloading for ' + dataset)
    return download_dataset

