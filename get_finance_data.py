import yfinance as yf
import backtrader as bt


def get_data(stock_name='AAPL', start='2015-01-01', end='205-12-25'):
    stock_names = stock_name.split()
    df = yf.download(stock_name, start=start, end=end, group_by='ticker')
    return df, stock_names
