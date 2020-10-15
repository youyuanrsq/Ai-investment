import backtrader as bt


class PrintClose(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close

    def next(self):
        self.log('Close: %.2f' % self.dataclose[0])


class MAcrossover(bt.Strategy):
    # 设置全局的交易策略参数
    params = (('pfast', 5), ('pslow', 81),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close

        self.order = None
        # 获取初始资金
        self.start_value = self.broker.get_value()
        # 实例化移动均值
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)


    def notify_order(self, order):
        # 如果order为submitted/accepted，返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed，报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                        成本:{order.executed.value},\
                        手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                        成本: {order.executed.value},\
                        手续费{order.executed.comm}')
            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    def next(self):
        '''
        当短期移动平均值向上穿过长期移动平均值时隔天买入，并在收益率达到10%后平仓
        :return:
        '''

        # 获取当前账户价值
        total_value = self.broker.get_value()
        # 计算收益率
        p_value = (total_value - self.start_value) / self.start_value

        # 检查是否有指令等待执行
        if self.order:
            return
        # 检查是否持仓
        if not self.position: # 没有持仓, 寻找买入信号
            total_value = self.broker.get_value()
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100
            if self.fast_sma[-1] > self.slow_sma[-1] and self.fast_sma[-2] < self.slow_sma[-2]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy(size=ss)

        else: # 持仓，寻找平仓信号
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
        # 获取MACD柱
        self.macdhist = bt.ind.MACDHisto(self.data,
                                         period_me1=self.p.p1,
                                         period_me2=self.p.p2,
                                         period_signal=self.p.p3)

    def notify_order(self, order):
        # 如果order为submitted/accepted，返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed，报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                                成本:{order.executed.value},\
                                手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                                成本: {order.executed.value},\
                                手续费{order.executed.comm}')
            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    def next(self):
        if not self.position:
            # 得到当前账户价值
            total_value = self.broker.get_value()
            # 1手等于100股，满仓买入
            ss = int((total_value / 100) / self.datas[0].close[0]) * 100
            # print(ss, total_value)
            # 当MACD柱大于0（红柱）且无持仓时满仓买入
            # print(self.macdhist[3])
            if self.macdhist > 0:
                self.order = self.buy(size=ss)
        else:
            # 当MACD柱小于0（绿柱）且持仓时全部清仓
            if self.macdhist < 0:
                self.close()


class TurtleStrategy(bt.Strategy):
    params = (
        ('long_period', 36),
        ('short_period', 7),
        ('printlog', False),
    )

    def __init__(self):
        self.order = None
        self.buyprice = 0
        self.buy_size = 0
        self.buy_count = 0

        # 海龟交易法则中的唐奇安通道和平均波幅ATR
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
            # 入场：价格突破上轨线且空仓时
        if self.buy_signal > 0 and self.buy_count == 0:
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.buy_count = 1
            self.order = self.buy()
            # 加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] and self.buy_count > 0 and self.buy_count <= 4:
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.order = self.buy()
            self.buy_count += 1
            # 离场：价格跌破下轨线且持仓时
        elif self.sell_signal < 0 and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0
            # 止损：价格跌破买入价的2个ATR且持仓时
        elif self.data.close < (self.buyprice - 2 * self.ATR[0]) and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0


    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')


    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')

            self.bar_executed = len(self)
        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})； \
        期末总资金: {self.broker.getvalue():.2f}', doprint=True)

