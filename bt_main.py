from get_finance_data import get_data
import backtrader as bt
from strategies import *
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--stock_name', default='SPY AAPL', help='stock name')
parser.add_argument('--strategy', default=BollStrategy, help='a defined strategy')
parser.add_argument('--start', default='2015-01-01', help='start date')
parser.add_argument('--end', default='2015-12-25', help='end date')
parser.add_argument('--start_cash', default=100000, help='start cash')
parser.add_argument('--qts', default=100, help='numer of transaction')
parser.add_argument('--commission', default=0.001, help='commission')


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


def main(stock_name, strategy, start, end, start_cash=100000, qts=500, com=0.001):
    # Instantiate Cerebro engine
    cerebro = bt.Cerebro()
    # get stock data
    data , stock_names = get_data(stock_name, start, end)
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
    # Set the trade size when using the turtle trading strategy
    # cerebro.addsizer(TraderSize)


    start_portfolio_value = cerebro.broker.get_value()

    cerebro.run()
    cerebro.plot()
    end_portfolio_value = cerebro.broker.get_value()
    pnl = end_portfolio_value - start_portfolio_value
    print('Starting Portfolio Value: %.2f' % start_portfolio_value)
    print('Final Portfolio Value: %.2f' % end_portfolio_value)
    print('PnL: %.2f' % pnl)


if __name__ == '__main__':
    args = parser.parse_args()
    main(stock_name=args.stock_name, strategy=args.strategy, start=args.start,
         end=args.end, start_cash=args.start_cash, qts=args.qts, com=args.commission)

