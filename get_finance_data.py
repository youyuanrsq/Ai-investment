import yfinance as yf
import backtrader as bt
import datetime
import pandas as pd
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json


def get_data(stock_name='AAPL', start='2015-01-01', end='2015-12-25',interval= '1m'):
    stock_names = stock_name.split()
    df = yf.download(stock_name, start=start, end=end, group_by='ticker', interval = interval)
    return df

def get_stock_price_info(ticker,period = '1y',interval = '1d',):
   data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = ticker,

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period = period,

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = interval,

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',

        # adjust all k line automatically
        # (optional, default is False)
        auto_adjust = True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )
   return data 


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def get_ticker():

    url = ("https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=NYSE&apikey=demo") 
    NYSE_company = get_jsonparsed_data(url)
    NYSE_company_info =  {}
    for i in NYSE_company:
        NYSE_company_info[i['symbol']] = i
    url = ("https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=NASDAQ&apikey=demo")
    NASDAQ_company = get_jsonparsed_data(url)
    NASDAQ_company_info =  {}
    for i in NASDAQ_company:
        NASDAQ_company_info[i['symbol']] = i
    url = ("https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=AMEX&apikey=demo")
    AMEX_company = get_jsonparsed_data(url)
    AEMX_company_info =  {}
    for i in AMEX_company:
        AEMX_company_info[i['symbol']] = i
    return NYSE_company_info, NASDAQ_company_info, AEMX_company_info




if __name__ == "__main__":
   day_data_path = '../trading_data/day_data/'
   tick_data_path = '../trading_data/tick_data/'
   data_type = 'tick'
   NYSE_company, NASDAQ_company, AEMX_company = get_ticker()
   if data_type == 'day':
      for symbol in NASDAQ_company.keys():
          al = get_stock_price_info(symbol, period='max')
          al.to_csv(day_data_path+symbol +'.CSV')
   if data_type == 'tick':
      for com in [NASDAQ_company,NYSE_company,AEMX_company]:
        for symbol in com.keys():
          al = get_stock_price_info(symbol, period='5d',interval = '1m' )
          al.to_csv(tick_data_path+symbol +'.CSV')
   if data_type == 'add_tick':
      for symbol in NASDAQ_company.keys():
          
          try: 
             print(symbol)
             bl = pd.read_csv(tick_data_path+symbol +'.CSV')  
             date_time_str = bl['Datetime'][bl['Datetime'].index.max()].split(' ')[0]
             start = datetime.datetime.strptime(date_time_str,'%Y-%m-%d') + datetime.timedelta(days=1.5)
             end = None 
             cl = get_data(stock_name=symbol, start=start, end=end)
             cl = bl.append(cl)
             cl.to_csv(tick_data_path+symbol +'.CSV') 
          except Exception as r:
             print(r)

