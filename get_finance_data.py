import yfinance as yf
import backtrader as bt
import json
from urllib.request import urlopen
import pandas as pd
import csv
import os

def get_data(stock_name='GE', start='2015-01-01', end='2015-12-25', date='2y'):
    stock_names = stock_name.split()
    df = yf.Ticker(stock_name).history(period=date)
    # try:
    #     df = yf.download(stock_name, start=start, end=end, group_by='ticker')
    # except:
    #     df = yf.Ticker(stock_name).history(period=date)

    return df, stock_names


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    data = json.loads(data)
    company_info = []
    for i in data:
        company_info.append(i['symbol'])
    return company_info


def download_stock_data(stock_name='AAPL', start='2015-01-01', end='2016-12-25', date='2y'):
    data, _ = get_data(stock_name=stock_name, start=start, end=end, date=date)
    main_path = 'D:\\pycharmprojects\\backtrader-general-api\\data\\stocks\\'
    path = main_path + stock_name + '.csv'
    data.to_csv(path)


def from_csv_read_company_name(file):
    company_name = []
    with open(file) as f:
        reader = csv.reader(f)
        for row in reader:
            company_name.append(row[0])

    return company_name


def from_local_read_company_name():
    filepath = 'D:\\pycharmprojects\\backtrader-general-api\\data\\stocks\\'
    filenames = os.listdir(filepath)
    company_names = []
    for filename in filenames:
        company = filename.split('.')[0]
        company_names.append(company)
    return company_names
