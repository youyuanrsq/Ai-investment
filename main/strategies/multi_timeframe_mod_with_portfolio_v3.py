import backtrader as bt
import os
import datetime
import pandas as pd
import csv
import sys
from Stop_loss import atr_range

def is_td(close_d, high_d):
    td = 1
    td_index = [[0, -4], [-1, -5], [-2. - 6], [-3, -7], [-4, -8], [-5, -9], [-6, 10], [-7, -11], [-8, -12], [-9, -13]]
    for i in td_index:
        if close_d[i[0]] < close_d[i[1]]:
            td = 0
    if td:
        six_seven_max = max(high_d[-2], high_d[-3])
        if high_d[0] > six_seven_max or high_d[-1] > six_seven_max:
            return True
        else:
            return False
    else:
        return False




def winter_summer_trading_time(date_now, year, month, day):
    if datetime.date(year, 3, 15) <= date_now < datetime.date(year, 11, 1):
        start_datetime = datetime.datetime(year, month, day, 9, 31, 0)
        end_datetime = datetime.datetime(year, month, day, 16, 0, 0)
        trade_datetime = datetime.datetime(year, month, day, 9, 31, 0)

    # 冬令时

    elif datetime.date(year, 11, 1) <= date_now <= datetime.date(year, 12, 31) or \
         datetime.date(year, 1, 1) <= date_now <= datetime.date(year, 3, 14):
         start_datetime = datetime.datetime(year, month, day, 10, 31, 0)
         end_datetime = datetime.datetime(year, month, day, 17, 0, 0)
         trade_datetime = datetime.datetime(year, month, day, 10, 31, 0)
    return start_datetime,  end_datetime, trade_datetime


class PortfolioModStrategy(bt.Strategy):
    '''
    混合粒度的多个回测策略
    假如使用resample如何加载数据才能保证在迭代时能准确取到
    同一个ticker的分钟和日线数据？
    加载一个分钟的行情数据然后接着resample，那么在BT中各个数据的下标
    分别是0，1表示第一个行情数据的分钟和日线，2,3表示第二个行情数据的
    分钟线和日线，以此类推。也即偶数包括0表示的是分钟数据，奇数表示的
    是日线数据

    改进：加入量能和九转
    '''

    params = dict(
        p_atr_period=14,
        fix_size=10,
        volume_rate=0.9,
        atr_level=0,
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = None
        self.atr_level = self.p.atr_level
        # 分别用不同的字典存储分钟和日线行情数据
        self.inds_m = dict()
        self.inds_d = dict()
        for i, d in enumerate(self.datas):
            if i == 0 or i % 2 == 0:
                self.inds_m[i] = dict()
                self.inds_m[i]['open'] = d.open
                self.inds_m[i]['close'] = d.close
                self.inds_m[i]['volume'] = d.volume
                self.inds_m[i]['accumulative_volume'] = 0
                # self.inds_m[i]['atr'] = bt.ind.AverageTrueRange(self.datas[i], period=self.p.p_atr_period)
                self.inds_m[i]['buy_signal'] = dict(three=0, four=0)
                self.inds_m[i]['buy_price'] = 0
                self.inds_m[i]['relative_min_price'] = list()
                self.inds_m[i]['relative_max_price'] = list()
                self.inds_m[i]['after_buy_high_price'] = 0  # 买入之后的高点
                self.inds_m[i]['last_buy_date'] = datetime.date(1, 1, 1)
                self.inds_m[i]['flag'] = False

            else:
                self.inds_d[i] = dict()
                self.inds_d[i]['open'] = d.open
                self.inds_d[i]['close'] = d.close
                self.inds_d[i]['low'] = d.low
                self.inds_d[i]['high'] = d.high
                self.inds_d[i]['volume'] = d.volume
                self.inds_d[i]['atr'] = bt.ind.AverageTrueRange(self.datas[i], period=self.p.p_atr_period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                self.buy_price = order.executed.price
                # self.log(order.executed.price)
            elif order.issell():
                pnl = order.executed.price - self.buy_price
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def find_relative_max_price(self, open_d, close_d):
        if open_d > close_d:
            return open_d
        else:
            return close_d


    def next(self):
        if self.order:
            return
        for i in range(0, len(self.datas), 2):
            # 初始化已经计算好的指标或者开高低收等数据可以创建新的引用简化代码，而临时变量不行
            open_m = self.inds_m[i]['open']
            close_m = self.inds_m[i]['close']
            volume_m = self.inds_m[i]['volume']
            close_d = self.inds_d[i + 1]['close']
            open_d = self.inds_d[i + 1]['open']
            low_d = self.inds_d[i + 1]['low']
            high_d = self.inds_d[i + 1]['high']
            volume_d = self.inds_d[i + 1]['volume']
            # atr = self.inds_m[i]['atr']
            atr = self.inds_d[i + 1]['atr']
            relative_max_price = self.inds_m[i]['relative_max_price']

            # 获取分钟行情数据的当前bar的年月日以及当前时间
            year = int(self.datas[i].datetime.datetime(0).year)
            month = int(self.datas[i].datetime.datetime(0).month)
            day = int(self.datas[i].datetime.datetime(0).day)
            date_now = self.datas[i].datetime.date(0)
            datetime_now = self.datas[i].datetime.datetime(0)
            start_datetime,  end_datetime, trade_datetime = winter_summer_trading_time(date_now, year, month, day)

            # 更新次低价
            if start_datetime == datetime_now:
                # 根据日线数据的阴阳线来更新次低价
                if close_d[0] < open_d[0]:
                    self.inds_m[i]['relative_min_price'].append(max(close_d[0], low_d[0]))
                    price = open_d[0]
                else:
                    self.inds_m[i]['relative_min_price'].append(max(open_d[0], low_d[0]))
                    price = close_d[0]
                relative_max_price_today = self.find_relative_max_price(open_d[0], close_d[0])
                self.inds_m[i]['relative_max_price'].append(relative_max_price_today)
        if len(self.inds_m[i]['relative_max_price']) >= 13:
            # 三段
            if relative_max_price[-2] > relative_max_price[-1]:
                self.inds_m[i]['buy_signal']['three'] = 1
            else:
                self.inds_m[i]['buy_signal']['three'] = 0

            # 四段
            if relative_max_price[-1] < relative_max_price[-2] < relative_max_price[-3] or \
                    relative_max_price[-2] < relative_max_price[-1] < relative_max_price[-3]:
                self.inds_m[i]['buy_signal']['four'] = 1
            else:
                self.inds_m[i]['buy_signal']['four'] = 0
            total_signal_value = 0
            for j in self.inds_m[i]['buy_signal'].values():
                total_signal_value += j

            # 在分钟数据上买卖，获取分钟行情数据的position
            position = self.getposition(self.datas[i]).size
            # 获取账户的现金
            cash = self.broker.get_cash()

            # print(self.data.datetime.datetime(0))

            # start_datetime = None
            # end_datetime = None
            # trade_datetime = None

            # 在盘中进行交易

            if start_datetime <= datetime_now <= end_datetime:
                self.inds_m[i]['accumulative_volume'] += volume_m[0]
                threshold = max(relative_max_price[-1], relative_max_price[-2])
                # 买入
                if total_signal_value > 0 and close_m[0] >= relative_max_price[-1] and \
                        self.inds_m[i]['last_buy_date'] < datetime.date(year, month, day) and \
                        self.inds_m[i]['accumulative_volume'] > volume_d[0] * self.p.volume_rate and position <= 0:
                    # print(self.inds_m[i]['accumulative_volume'], volume_d[-1])
                    self.inds_m[i]['last_buy_date'] = datetime.date(year, month, day)
                    self.inds_m[i]['flag'] = True
                    self.inds_m[i]['buy_price'] = close_m[0]

                    self.buy(data=self.datas[i], price=close_m[0], size=self.p.fix_size)
                elif total_signal_value > 0 and close_m[0] >= threshold and \
                        self.inds_m[i]['last_buy_date'] < datetime.date(year, month, day) and \
                        self.inds_m[i]['accumulative_volume'] > volume_d[0] * self.p.volume_rate and position <= 0:
                    # size = int(cash / close_m[0] * 0.7)
                    # print(size)
                    self.inds_m[i]['last_buy_date'] = datetime.date(year, month, day)
                    self.inds_m[i]['flag'] = True
                    self.inds_m[i]['buy_price'] = close_m[0]
                    self.buy(data=self.datas[i], price=close_m[0], size=self.p.fix_size)
                # ATR 止损
                atr_flag = atr_range(atr[0], self.atr_level, self.inds_m[i]['relative_min_price'][-1])
                if (open_m[0] < atr_flag or close_m[0] < atr_flag) and position > 0:
                    if date_now > self.inds_m[i]['last_buy_date']:
                        self.sell(data=self.datas[i], size=position)
                        self.inds_m[i]['flag'] = False

                # # # 防止阴跌止损
                # elif close_m[0] <= self.inds_m[i]['after_buy_high_price'] * (1 - 0.1) and position > 0:
                #     self.sell(data=self.datas[i], size=position)
                #     self.inds_m[i]['flag'] = False
                # 日内止损
                # if close_m[0] <= self.inds_m[i]['buy_price'] * (1 - 0.01) and position > 0:
                #     self.sell(data=self.datas[i], size=position)
                #     self.inds_m[i]['flag'] = False
                # 九转序列
                # is_td = self.is_td(close_d, high_d)
                # if is_td and position > 0:
                #     self.sell(data=self.datas[i], size=position)
                #     self.inds_m[i]['flag'] = False
                #     print('jiuzhuan')
            else:
                self.inds_m[i]['accumulative_volume'] = 0
        # 更新次高价, 每天只更新一次，所以在开盘时更新
        # if datetime_now == start_datetime:
        # relative_max_price_today = self.find_relative_max_price(open_d[0], close_d[0])
        # self.inds_m[i]['relative_max_price'].append(relative_max_price_today)
        # print(self.inds_m[i]['relative_max_price'])

        # 更新买入后的高点， 买入后更新，卖出后清零重头算起
        if self.inds_m[i]['flag']:
            if self.inds_m[i]['after_buy_high_price'] < self.inds_m[i]['relative_max_price'][-1]:
                self.inds_m[i]['after_buy_high_price'] = self.inds_m[i]['relative_max_price'][-1]
        else:
            self.inds_m[i]['after_buy_high_price'] = 0


def from_local_read_company_name(filepath='D:\\pycharmprojects\\backtrader-general-api\\data\\stocks\\'):
    filenames = os.listdir(filepath)
    company_names = []
    for filename in filenames:
        temp = filename.split('.')
        if len(temp) > 2:
            company = temp[0] + '.' + temp[1]
        else:
            company = temp[0]
        company_names.append(company)
    return company_names


def load_data(data_path):
    df = pd.read_csv(data_path, skiprows=0, header=0)
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_index(ascending=False)
    return df


def main(symbols, data_path_1m, data_path_1d, p_atr_period, volume_rate, atr_level):
    cerebro = bt.Cerebro()
    # cerebro = bt.MyCerebro()
    for symbol in symbols:
        # 加载分钟线数据
        data_path = os.path.join(data_path_1m, f'{symbol}.CSV')
        df = load_data(data_path)
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=0,  # 使用索引列作日期列
            open=1,  # 开盘价所在列
            high=2,  # 最高价所在列
            low=3,  # 最低价所在列
            close=4,  # 收盘价价所在列
            volume=5,  # 成交量所在列
            openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
            fromdate=datetime.datetime(2020, 10, 8),
            todate=datetime.datetime(2021, 3, 26),
            timeframe=bt.TimeFrame.Minutes
        )
        # 至少要有60000根bar
        if len(df) > 60000:
            # print(symbol)
            data_path = os.path.join(data_path_1d, f'{symbol}.CSV')
            df2 = load_data(data_path)

            data2 = bt.feeds.PandasData(
                dataname=df2,
                datetime=0,  # 使用索引列作日期列
                open=1,  # 开盘价所在列
                high=2,  # 最高价所在列
                low=3,  # 最低价所在列
                close=4,  # 收盘价价所在列
                volume=5,  # 成交量所在列
                openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
                fromdate=datetime.datetime(2020, 10, 8),
                todate=datetime.datetime(2021, 3, 26),
                timeframe=bt.TimeFrame.Days
            )
            cerebro.adddata(data)
            cerebro.adddata(data2)
        else:
            continue

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addstrategy(PortfolioModStrategy, p_atr_period=p_atr_period, volume_rate=volume_rate, atr_level=atr_level)
    cerebro.broker.set_cash(100000.)
    cerebro.broker.set_coc(True)
    cerebro.broker.set_slippage_fixed(fixed=5)
    cerebro.broker.set_slippage_perc(perc=0.05)
    # 设置佣金为千分之一
    # cerebro.broker.setcommission(commission=0.000)
    start_portfolio_value = cerebro.broker.get_value()
    results = cerebro.run(load_data_from_pkl=True, save_data_to_pkl=False, pkl_path='../pkl_data/data.pkl')
    # results = cerebro.run()
    sharpe_ratio = results[0].analyzers.sharperatio.get_analysis()['sharperatio']
    annual_return = results[0].analyzers.returns.get_analysis()['rnorm100']
    max_drawdown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
    total_trade = results[0].analyzers.tradeanalyzer.get_analysis()['total']['closed']
    gross_pnl = results[0].analyzers.tradeanalyzer.get_analysis()['pnl']['gross']['total']
    won = results[0].analyzers.tradeanalyzer.get_analysis()['won']['total']
    won_rate = won / total_trade
    print('sharpe_ratio', sharpe_ratio, 'max_drawdown', max_drawdown, 'gross_pnl', gross_pnl, 'won', won, 'won_rate',
          won_rate)

    with open('multi_timeframe_mod_with_portfolio_v3_test7.txt', 'a+') as f:
        f.writelines('atr_period:' + str(p_atr_period) + ' ')
        f.writelines('volume_rate:' + str(volume_rate) + ' ')
        f.writelines('atr_level:' + str(atr_level) + ' ')
        f.writelines('sharpe_ratio:' + str(sharpe_ratio) + ' ')
        # f.writelines('sharpe_ratio:' + str(sharpe_ratio) + ' ')
        f.writelines('max_drawdown:' + str(max_drawdown) + ' ')
        f.writelines('total_trade:' + str(total_trade) + ' ')
        f.writelines('gross_pnl:' + str(gross_pnl) + ' ')
        f.writelines('won:' + str(won) + ' ')
        f.writelines('won_rate:' + str(won_rate) + '\n')
    # cerebro.plot(style='candle')


def floatrange(start, stop, steps):
    return [start + float(i) * (stop - start) / (float(steps) - 1) for i in range(steps)]


if __name__ == '__main__':
    data_path_1m = '../../test_data/1min/'
    data_path_1d = '../../test_data/day/'
    symbols = from_local_read_company_name(data_path_1d)
    # main(symbols=symbols, data_path_1m=data_path_1m, data_path_1d=data_path_1d, p_atr_period=10, volume_rate=0.6, atr_level=1.2)

    for atr_period in range(7, 15):
        for volume_rate in floatrange(0.5, 1.5, 11):
            for atr_level in floatrange(0.5, 1.2, 8):
                main(symbols=symbols, data_path_1m=data_path_1m, data_path_1d=data_path_1d, p_atr_period=atr_period,
                     volume_rate=volume_rate, atr_level=atr_level)
