from get_finance_data import get_data, get_jsonparsed_data
import backtrader as bt
from strategies import *
import argparse
import random
import csv
import os


parser = argparse.ArgumentParser()
parser.add_argument('--stock_name', default='GE', help='stock name')
parser.add_argument('--strategy', default=VolumeStrategy, help='a defined strategy')
parser.add_argument('--start', default='2015-01-01', help='start date')
parser.add_argument('--end', default='2017-12-25', help='end date')
parser.add_argument('--start_cash', default=100000, help='start cash')
parser.add_argument('--qts', default=100, help='numer of transaction')
parser.add_argument('--commission', default=0.001, help='commission')
parser.add_argument('--url', default='https://financialmodelingprep.com/api/v3/search?query=&limit=100000&exchange=NYSE&apikey=demo')


class TraderSize(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return self.p.stake
        position = self.broker.getposition()
        if not position.size:
            return 0
        else:
            return position.size


def from_csv_read_company_name(file):
    company_name = []
    with open(file) as f:
        reader = csv.reader(f)
        for row in reader:
            company_name.append(row[0])

    return company_name


def main(stock_name, strategy, start, end, start_cash=100000, qts=500, com=0.001):
    # Instantiate Cerebro engine
    cerebro = bt.Cerebro()
    # get stock data
    data, stock_names = get_data(stock_name, start, end)
    # load data to Cerebro
    if len(stock_names) > 1:
        for i in stock_names:
            feed = bt.feeds.PandasData(dataname=data[i])
            cerebro.adddata(feed)
    else:
        feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(feed)
    # Add strategy to Cerebro
    cerebro.addstrategy(strategy)
    # set startcash and commission
    cerebro.broker.set_cash(start_cash)
    cerebro.broker.setcommission(commission=com)
    # Set the trade size
    # cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    start_portfolio_value = cerebro.broker.get_value()

    cerebro.run()
    # cerebro.plot()
    end_portfolio_value = cerebro.broker.get_value()
    pnl = end_portfolio_value - start_portfolio_value
    print('Starting Portfolio Value: %.2f' % start_portfolio_value)
    print('Final Portfolio Value: %.2f' % end_portfolio_value)
    print('PnL: %.2f' % pnl)
    return pnl


if __name__ == '__main__':
    args = parser.parse_args()
    company_name = get_jsonparsed_data(args.url)
    path = os.getcwd()
    # company_name = from_csv_read_company_name(path + '\\data\\file.csv')
    stocks_run_data = []
    count = 0
    positive_count = 0
    while count < 100:
        index = random.randint(0, len(company_name))
        stock_name = company_name[index]
        try:
            Pnl = main(stock_name=stock_name, strategy=args.strategy, start='2015-01-01',
                           end='2018-12-25')
        except:
            # count += 1
            continue
        stocks_run_data.append((stock_name, Pnl))
        if Pnl > 0:
            positive_count += 1
        count += 1
        print('{} stocks completed'.format(count))

    print('There are {} stocks out of 100 that have a positive Pnl and {} are negative'
          .format(positive_count, 100-positive_count))

    with open(path + '\\data\\file.csv', 'w') as f:
        writer = csv.writer(f)
        for i in stocks_run_data:
            writer.writerow(i)
