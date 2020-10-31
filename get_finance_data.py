import yfinance as yf
import backtrader as bt
import json
from urllib.request import urlopen


def get_data(stock_name='AAPL', start='2015-01-01', end='2015-12-25'):
    stock_names = stock_name.split()
    # df = yf.download(stock_name, start=start, end=end, group_by='ticker')
    try:
        df = yf.Ticker(stock_name).history(period='5y')
    except:
        pass

    return df, stock_names


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    data = json.loads(data)
    company_info = []
    for i in data:
        company_info.append(i['symbol'])
    return company_info



