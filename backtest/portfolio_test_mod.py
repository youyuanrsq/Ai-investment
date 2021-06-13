import backtrader as bt
import os
import datetime
import matplotlib.pyplot as plt

class ModStrategy(bt.Strategy):
    params = dict(
        macd_p1=10,
        macd_p2=31,
        macd_p3=5,
        p_fast=5,
        p_slow=25,
        p_atr_period=14,
        cci_window=30,
        cci_level=10
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = None
        self.inds = dict()
        for d in self.datas:
            self.inds[d] = dict()
            self.inds[d]['open'] = d.open
            self.inds[d]['close'] = d.close
            self.inds[d]['high'] = d.high
            self.inds[d]['low'] = d.low
            self.inds[d]['buy_signal'] = 0
            self.inds[d]['base_line'] = 0
            self.inds[d]['buy_price'] = list()
            self.inds[d]['min_price'] = 0
            self.inds[d]['atr'] = bt.ind.AverageTrueRange(d, period=self.p.p_atr_period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                # self.buy_price = order.executed.price
                # self.log(order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        if self.order:
            return
        # ***************** 三段战法 *****************
        # 阴阴阳
        for i, d in enumerate(self.datas):
            # 阴阴阳
            # if self.inds[d]['close'][-2] <= self.inds[d]['open'][-2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][
            #     -1] and self.inds[d]['close'][0] >= self.inds[d]['open'][0] \
            #         and self.inds[d]['open'][-2] > self.inds[d]['open'][-1] and self.inds[d]['open'][-2] < \
            #         self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0

            # 阴阳阳
            # if self.inds[d]['close'][-2] <= self.inds[d]['open'][-2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][
            #     -1] and self.inds[d]['close'][0] >= self.inds[d]['open'][0] \
            #         and self.inds[d]['open'][-2] > self.inds[d]['open'][-1] and self.inds[d]['open'][-2] < \
            #         self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            # 阴阳阴
            if self.inds[d]['close'][-2] <= self.inds[d]['open'][-2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][
                -1] and self.inds[d]['close'][0] <= self.inds[d]['open'][0] \
                    and self.inds[d]['open'][-2] > self.inds[d]['open'][-1] and self.inds[d]['open'][-2] < \
                    self.inds[d]['open'][0]:
                self.inds[d]['buy_signal'] = 1
            else:
                self.inds[d]['buy_signal'] = 0

            # # 四段战法
            # # 阴阴阳阳
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][-3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['close'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['open'][-2] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            # # 阴阴阳阴
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['close'][-1] < self.inds[d]['open'][0] \
            #         and self.inds[d]['open'][-1] < self.inds[d]['close'][0] and self.inds[d]['open'][-2] < \
            #         self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['open'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['open'][-2] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['open'][-1] < self.inds[d]['open'][0] \
            #         and self.inds[d]['open'][-3] < self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['open'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['open'][-3] < self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['close'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['close'][-2] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['close'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['open'][-3] < self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] <= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['open'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['open'][-3] < self.inds[d]['close'][0] \
            #         and self.inds[d]['open'][-1] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['open'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['open'][-1] < self.inds[d]['close'] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['open'][-1] < self.inds[d]['close'][0] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] <= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['open'][-2] and self.inds[d]['close'][-1] < self.inds[d]['open'][0] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['close'][-1] < self.inds[d]['open'][0] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] >= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['close'][-2] > self.inds[d]['close'][-1] \
            #         and self.inds[d]['close'][-1] < self.inds[d]['close'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] <= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['open'][-1] < self.inds[d]['open'][0] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0
            #
            # if self.inds[d]['close'][-3] >= self.inds[d]['open'][3] and self.inds[d]['close'][-2] >= self.inds[d]['open'][
            #     -2] and self.inds[d]['close'][-1] <= self.inds[d]['open'][-1] \
            #         and self.inds[d]['close'][0] >= self.inds[d]['open'][0] and self.inds[d]['close'][-3] > \
            #         self.inds[d]['close'][-2] and self.inds[d]['open'][-1] < self.inds[d]['open'][0] \
            #         and self.inds[d]['close'][-3] < self.inds[d]['open'][0]:
            #     self.inds[d]['buy_signal'] = 1
            # else:
            #     self.inds[d]['buy_signal'] = 0

            position = self.getposition(d).size
            if self.inds[d]['buy_signal'] > 0:
                self.buy(d)
                try:
                    self.inds[d]['buy_price'].append(self.inds[d]['high'][1])
                except:
                    pass

            # # 固定比例止盈
            if len(self.inds[d]['buy_price']) > 0:
                self.inds[d]['min_price'] = min(self.inds[d]['buy_price'])
            if self.inds[d]['close'] >= self.inds[d]['min_price'] * 1.2 and position > 0:
                self.sell(d)
                self.inds[d]['buy_price'].remove(self.inds[d]['min_price'])





def main(data_path, symbol, save_log_path):
    cerebro = bt.Cerebro()

    data = bt.feeds.GenericCSVData(
        dataname=os.path.join(data_path, f'{symbol}.CSV'),
        fromdate=datetime.datetime(2016, 3, 14),
        todate=datetime.datetime(2021, 3, 12),
        nullvalue=0.0,
        dtformat=('%Y-%m-%d'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )
    cerebro.adddata(data)

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addstrategy(ModStrategy)
    cerebro.broker.set_cash(1000000.)
    # cerebro.broker.set_coc(True)
    cerebro.broker.set_slippage_fixed(fixed=5)
    cerebro.broker.set_slippage_perc(perc=0.05)
    # 设置交易单位大小
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # 设置佣金为千分之一
    cerebro.broker.setcommission(commission=0.000)
    cerebro.run()
    cerebro.plot()
    plt.savefig(save_log_path+'/'+symbol+'.png')


if __name__ == '__main__':
    symbol = 'FUTU'
    date_time = str(datetime.date.today())
    data_path = '../trading_data/day_data/'
    save_log_path = '../trading_log/' + date_time
    if not os.path.isdir(save_log_path): 
       print('new directry has been created')
       os.system('mkdir '+save_log_path)
    main(data_path, symbol,save_log_path)
