import backtrader as bt
import datetime

class PrintClose(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close

    def next(self):
        self.log('Close: %.2f' % self.dataclose[0])


class MAcrossover(bt.Strategy):
    # Moving average parameters
    params = (('pfast', 5), ('pslow', 81),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        # Order variable will contain ongoing order details/status
        self.order = None

        self.start_value = self.broker.get_value()
        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):

        total_value = self.broker.get_value()
        p_value = (total_value - self.start_value) / self.start_value

        if self.order:
            return
        # Check if we are in the market
        if not self.position: # We are not in the market, look for a signal to OPEN trades
            total_value = self.broker.get_value()
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100
            if self.fast_sma[-1] > self.slow_sma[-1] and self.fast_sma[-2] < self.slow_sma[-2]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy(size=ss)

        else: # We are already in the market, look for a signal to CLOSE trades
            if p_value > 0.1:
                self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()


class Screener_SMA(bt.Analyzer):
    params = (('period', 20), ('devfactor', 2),)

    def start(self):
        self.bbands = {
            data: bt.indicators.BollingerBands(data, period=self.params.period, devfactor=self.params.devfactor)
            for data in self.datas}

    def stop(self):
        self.rets['over'] = list()
        self.rets['under'] = list()

        for data, band in self.bbands.items():
            node = data._name, data.close[0], round(band.lines.bot[0], 2)
            if data > band.lines.bot:
                self.rets['over'].append(node)
            else:
                self.rets['under'].append(node)


class AverageTrueRange(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

    def next(self):
        range_total = 0
        for i in range(-13, 1):
            true_range = self.datahigh[i] - self.datalow[i]
            range_total += true_range
        ATR = range_total / 14

        self.log('Close: %.2f, ATR: %.4f' % (self.dataclose[0], ATR))


class BtcSentiment(bt.Strategy):
    params = (('period', 10), ('devfactor', 1),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.btc_price = self.datas[0].close
        self.google_sentiment = self.datas[1].close
        self.bbands = bt.indicators.BollingerBands(self.google_sentiment, period=self.params.period,
                                                   devfactor=self.params.devfactor)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):

        if self.order:
            return

        if self.google_sentiment > self.bbands.lines.top[0]:

            if not self.position:
                self.log('Google Sentiment Value: %.2f' % self.google_sentiment[0])
                self.log('Top band: %.2f' % self.bbands.lines.top[0])
                # We are not in the market, we will open a trade
                self.log('***BUY CREATE, %.2f' % self.btc_price[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        elif self.google_sentiment < self.bbands.lines.bot[0]:
            # Check if we are in the market
            if not self.position:
                self.log('Google Sentiment Value: %.2f' % self.google_sentiment[0])
                self.log('Bottom band: %.2f' % self.bbands.lines.bot[0])
                # We are not in the market, we will open a trade
                self.log('***SELL CREATE, %.2f' % self.btc_price[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

        else:
            if self.position:
                # We are in the market, we will close the existing trade
                self.log('Google Sentiment Value: %.2f' % self.google_sentiment[0])
                self.log('Bottom band: %.2f' % self.bbands.lines.bot[0])
                self.log('Top band: %.2f' % self.bbands.lines.top[0])
                self.log('CLOSE CREATE, %.2f' % self.btc_price[0])
                self.order = self.close()


class MACDStrategy(bt.Strategy):
    params = (('p1', 19), ('p2', 31), ('p3', 5),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))  # Comment this line when running optimization

    def __init__(self):
        self.order = None
        # get MACD
        self.macdhist = bt.ind.MACDHisto(self.data,
                                         period_me1=self.p.p1,
                                         period_me2=self.p.p2,
                                         period_signal=self.p.p3)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        if not self.position:
            total_value = self.broker.get_value()
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100

            if self.macdhist > 0:
                self.order = self.buy(size=ss)
        else:
            if self.macdhist < 0:
                self.close()


class TurtleStrategy(bt.Strategy):
    params = (
        ('long_period', 36),
        ('short_period', 7),
        ('printlog', True),
    )

    def __init__(self):
        self.order = None
        self.buyprice = 0
        self.buy_size = 0
        self.buy_count = 0

        self.H_line = bt.indicators.Highest(self.data.high(-1), period=self.p.long_period)
        self.L_line = bt.indicators.Lowest(self.data.low(-1), period=self.p.short_period)
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))
        self.ATR = bt.indicators.MovingAverageSimple(self.TR, period=14)

        self.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.sell_signal = bt.ind.CrossOver(self.data.close(0), self.L_line)

    def next(self):
        if self.order:
            return

        if self.buy_signal > 0 and self.buy_count == 0:
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.buy_count = 1
            self.order = self.buy()

        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] and self.buy_count > 0 and self.buy_count <= 4:
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.order = self.buy()
            self.buy_count += 1

        elif self.sell_signal < 0 and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0

        elif self.data.close < (self.buyprice - 2 * self.ATR[0]) and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0


    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None


class BollStrategy(bt.Strategy):
    params = (('p_period_volume', 10),
              ('p_sell_ma', 5),
              ('p_oneplot', False),
              ('pstake', 100))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            # Brin middle rail
            boll_mid = bt.ind.BBands(d.close).mid
            # buy signal
            self.inds[d]['buy_con'] = bt.And(
                d.open < boll_mid, d.close > boll_mid,
                d.volume == bt.ind.Highest(d.volume, period=self.p.p_period_volume, plot=False)
            )
            # sell signal
            self.inds[d]['sell_con'] = d.close < bt.ind.SMA(d.close, period=self.p.p_sell_ma)

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            total_value = self.broker.get_value()
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100
            pos = self.getposition(d).size
            if not pos:
                if self.inds[d]['buy_con']:
                    self.buy(data=d, size=ss)
            elif self.inds[d]['sell_con']:
                self.close(data=d)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None


class BuyingGainAndSellingLossesStrategy(bt.Strategy):
    '''
    A selling strategy of buying gains and selling losses for consecutive declines
    '''
    params = dict(
        p_downdays=4, # Consecutive days of decline
        p_period_volume=10,
        p_stoploss=0.082, # Stop loss ratio
        p_takeprofit=0.116, # Check surplus proportion
        limit=0.005,
        limdays=3,
        limdays2=1000,
        r=0.25,
        hold=10,
        usebracket=False, # use order_target_size
        switchp1p2=False # switch prices of order1 and order2
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.orefs = list()
        self.buy_signal = self.datas[0].volume == bt.ind.Highest(self.datas[0].volume, period=self.p.p_period_volume, plot=False)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if self.orefs: # order list
            return

        if not self.position:
            # Obtain the closing price in recent days to determine whether the continuous decline
            lastcloses = list()
            total_value = self.broker.get_value()
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100
            # for i in range(self.p.p_downdays + 1):
            #     lastcloses.append(self.dataclose[-i])
            r = (self.dataclose[-self.p.p_downdays] - self.dataclose[0])/self.dataclose[-self.p.p_downdays]
            # N consecutive days down And the day's closing price did not fall below 20 percent from N days earlier
            # if lastcloses == sorted(lastcloses) and r < self.p.r:
            if self.buy_signal and lastcloses == sorted(lastcloses) and r < self.p.r:
                # Calculate the buy offer P1, stop loss P2, and stop gain P3
                close = self.dataclose[0]
                p1 = close * (1.0 - self.p.limit)
                p2 = p1 - self.p.p_stoploss * close
                p3 = p1 + self.p.p_takeprofit * close
                # Calculate order validity
                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = valid3 = datetime.timedelta(self.p.limdays2)
                # The bracket orders is used to set purchases and sales
                os = self.buy_bracket(
                    price=p1, valid=valid1,
                    stopprice=p2, stopargs=dict(valid=valid2),
                    limitprice=p3, limitargs=dict(valid=valid3),
                    size=ss,
                )
                # Save the active order
                self.orefs = [o.ref for o in os]

    def notify_order(self, order):
        print('{}: Order ref: {} / Type{} / Status {}'.format(
            self.datetime.date(0),
            order.ref, 'Buy' * order.isbuy() or 'Sell',
            order.getstatusname()
        ))

        if order.status == order.Completed:
            self.holdstart = len(self)

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)


class VolumeStrategy(bt.Strategy):
    params = (('p_period_volume', 5),
              ('p_sell_ma', 7),
              ('p_r', 4),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.inds = dict()
        self.start_value = self.broker.get_value()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.highest_volume = bt.ind.Highest(d.volume, period=self.p.p_period_volume, plot=False)
            # buy signal
            self.inds[d]['buy_con'] = d.volume == self.highest_volume
            # sell signal

            self.inds[d]['sell_con'] = bt.And(
                d.volume <= self.highest_volume//self.p.p_r, d.volume > self.highest_volume//(self.p.p_r+1),
                d.close < bt.ind.SMA(d.close, period=self.p.p_sell_ma)
            )
    def next(self):
        for i, d in enumerate(self.datas):
            total_value = self.broker.get_value()
            p_value = (total_value - self.start_value) / self.start_value
            self.start_value = total_value
            total_value = self.broker.get_value()
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100
            pos = self.getposition(d).size

            if not pos:
                if self.inds[d]['buy_con']:
                    self.buy(data=d, size=ss)
            elif self.inds[d]['sell_con']:
                self.close(data=d)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

class MainStrategy(bt.Strategy):
    params = (
        ('p_stake', 100),
        ('macd_p1', 29),
        ('macd_p2', 47),
        ('macd_p3', 5),
        ('p_period_volume', 5),
        ('p_sell_ma', 8),
        ('p_period_brin', 7),
        ('buy_limit_percent', 0.01),
        ('buy_valid_date', 5),
        ('stoptype', bt.Order.StopTrail),
        ('trailamount', 0.0),
        ('trailpercent', 0.05),
        ('p_downdays', 4),
        ('p_fast', 12),
        ('p_slow', 15)

    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))  # Comment this line when running optimization

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datavolume = self.datas[0].volume
        self.positive = 0
        self.negative = 0
        self.pre_value = 0.0
        # MACD
        self.macdhist = bt.ind.MACDHisto(self.data,
                                         period_me1=self.p.macd_p1,
                                         period_me2=self.p.macd_p2,
                                         period_signal=self.p.macd_p3)
        # Brin middle rail
        boll_mid = bt.ind.BBands(self.dataclose, period=self.p.p_period_brin).mid
        # Brin buy signal
        self.brin_volume = bt.And(
            self.dataopen < boll_mid, self.dataclose > boll_mid,
            self.datavolume == bt.ind.Highest(self.datavolume, period=self.p.p_period_volume, plot=False)
        )
        self.brin_sell = self.dataclose < bt.ind.SMA(self.dataclose, period=self.p.p_sell_ma)
        # SMA
        self.slowSMA = bt.ind.SMA(period=self.p.p_slow)
        self.fastSMA = bt.ind.SMA(period=self.p.p_fast)
        self.SMA_Cross = bt.ind.CrossOver(self.slowSMA, self.fastSMA)

    def notify_order(self, order):
        # print('price', order.executed.price)
        if order.status in [order.Completed]:
            print('Completed order: {}: Order ref: {} / Type {} / Status {} '.format(
                self.data.datetime.date(0),
                order.ref, 'Buy' * order.isbuy() or 'Sell',
                order.getstatusname()))
            if order.isbuy():
                self.pre_value = order.executed.value
            if order.issell():
                if order.executed.value - self.pre_value >= 0:
                    self.positive += 1
                else:
                    self.negative += 1
                # self.pre_value = order.executed.value
            print('Positive: {}, Negtive: {}'.format(self.positive, self.negative))

            self.order = None
        if order.status in [order.Expired]:
            self.order = None
        print('{}: Order ref: {} / Type {} / Status {}'.format(
            self.data.datetime.date(0),
            order.ref, 'Buy' * order.isbuy() or 'Sell',
            order.getstatusname()))

    def next(self):
        total_value = self.broker.get_value()
        ss = int((total_value / 100) / self.datas[0].close[0]) * 100
        if not self.position:
            if None == self.order:
                # consecutive declines
                lastcloses = list()
                for i in range(self.p.p_downdays + 1):
                    lastcloses.append(self.dataclose[-i])

                if self.macdhist > 0 and self.brin_volume and self.SMA_Cross > 0:
                    self.order = self.buy(size=ss)


        elif self.order is None:
            # if self.macdhist < 0 and self.SMA_Cross < 0 and self.brin_sell:
            #     self.order = self.close()

            if self.macdhist < 0:
                # self.order = self.sell(size=self.p.p_stake)
                self.order = self.close()
            elif self.SMA_Cross < 0:
                self.order = self.close()
                # self.order = self.sell(size=self.p.p_stake)
            elif self.brin_sell:
                self.order = self.close()
