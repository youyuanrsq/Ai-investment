from typing import List, Dict
import datetime
from operator import itemgetter
from math import log10
from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine
from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy.trader.object import TickData, BarData
from vnpy.trader.constant import Interval


'''
该文件应在portfolio_strategy/strategies目录下
'''

class MultiTimeframePortfolioStrategy(StrategyTemplate):
    """"""
    author = "youyuan"

    atr_period = 7
    volume_rate = 0.6
    atr_level = 1.2
    fix_size = 1
    last_tick_time = None
    last_bar_time = None
    accumulative_volume = {}
    buy_signal = {}
    count = {}
    relative_min_price = {}
    relative_max_price = {}
    window_bars = {}
    parameters = ["atr_period", "volume_rate", "atr_level", 'fix_size']
    last_buy_price = {}
    last_sell_price = {}
    open_d = {}
    close_d = {}
    volume_d = {}
    high_d = {}
    low_d = {}
    atr = {}

    def __init__(
        self,
        strategy_engine: StrategyEngine,
        strategy_name: str,
        vt_symbols: List[str],
        setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)

        self.bgs: Dict[str, BarGenerator] = {}
        self.ams: Dict[str, ArrayManager] = {}
        self.bg_dailys = {}
        self.am_dailys = {}
        self.last_tick_time: datetime = None

        # Obtain contract info
        for vt_symbol in self.vt_symbols:
            self.bgs[vt_symbol] = BarGenerator(self.on_bar)
            self.ams[vt_symbol] = ArrayManager(size=15)
            self.bg_dailys[vt_symbol] = BarGenerator(self.on_bar, 1, self.on_daily_bar, Interval.DAILY)
            self.am_dailys[vt_symbol] = ArrayManager(size=15)
            self.accumulative_volume[vt_symbol] = 0
            self.buy_signal[vt_symbol] = dict(three=0, four=0)
            self.count[vt_symbol] = 1
            self.relative_max_price[vt_symbol] = list()
            self.relative_min_price[vt_symbol] = list()
            self.last_buy_price[vt_symbol] = 0
            self.last_sell_price[vt_symbol] = 0
            self.atr[vt_symbol] = 0

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        self.load_bars(30)

    def on_bar(self, bar: BarData):
        """"""
        pass

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        if (
            self.last_tick_time
            and self.last_tick_time.minute != tick.datetime.minute
        ):
            bars = {}
            for vt_symbol, bg in self.bgs.items():
                bars[vt_symbol] = bg.generate()
            self.on_bars(bars)

        bg: BarGenerator = self.bgs[tick.vt_symbol]
        bg.update_tick(tick)

        self.last_tick_time = tick.datetime

    def on_daily_bar(self, bar):
        self.window_bars[bar.vt_symbol] = bar
        # 确保将所有symbol的数据都接收到
        if len(self.window_bars.keys()) == len(self.vt_symbols):
            self.on_daily_bars(self.window_bars)
            self.window_bars = {}
            # print(self.window_bars)

    def on_bars(self, bars: Dict[str, BarData]):
        """"""
        # self.cancel_all()
        for vt_symbol, bar in bars.items():
            bg_daily = self.bg_dailys[vt_symbol]
            bg_daily.update_bar(bar)
        for vt_symbol, bar in bars.items():
            # bg_daily = self.bg_dailys[vt_symbol]
            # bg_daily.update_bar(bar)
            am = self.ams[vt_symbol]
            am.update_bar(bar)
            am_daily = self.am_dailys[vt_symbol]
            if not am.inited:
                return
            if not am_daily.inited:
                return
            # 获取分钟行情数据当前bar的年月日以及当前时间
            year = int(bar.datetime.year)
            month = int(bar.datetime.month)
            day = int(bar.datetime.day)
            date_now = bar.datetime.date()
            datetime_now = datetime.datetime.strptime(str(bar.datetime)[0:19], "%Y-%m-%d %H:%M:%S")
            time_str = str(bar.datetime)[0:19]
            # 夏令时
            if datetime.date(year, 3, 15) <= date_now < datetime.date(year, 11, 1):
                start_datetime = datetime.datetime(year, month, day, 9, 31, 0)
                last_five_min = datetime.datetime(year, month, day, 15, 54, 0)
                end_datetime = datetime.datetime(year, month, day, 15, 59, 0)
            # 冬令时
            elif datetime.date(year, 11, 1) <= date_now <= datetime.date(year, 12, 31) or \
                    datetime.date(year, 1, 1) <= date_now <= datetime.date(year, 3, 14):
                start_datetime = datetime.datetime(year, month, day, 10, 31, 0)
                last_five_min = datetime.datetime(year, month, day, 16, 54, 0)
                end_datetime = datetime.datetime(year, month, day, 16, 59, 0)
            # 获取日线成交数据
            open_d = am_daily.open
            close_d = am_daily.close
            high_d = am_daily.high
            low_d = am_daily.low
            volume_d = am_daily.volume

            # 获取分钟线行情数据
            open_m = am.open
            close_m = am.close
            volume_m = am.volume
            low_m = am.low
            high_m = am.high

            # 获取日线数据的atr
            atr = am_daily.atr(self.atr_period, array=True)
            # 更新次高价的初始值以及次低价，每天只更新一次，在开盘时更新
            if datetime_now == start_datetime:
                # self.open = open_m[-1]
                # self.pre_open = open_d[-1]
                # self.pre_close = close_d[-1]
                relative_max_price_today = self.find_relative_max_price(open_d[-1], close_d[-1])
                self.relative_max_price[vt_symbol].append(relative_max_price_today)
                # print(bar.datetime, relative_max_price_today, open_d[-1], close_d[-1])
                # print(self.relative_max_price[vt_symbol])
                self.atr[vt_symbol] = atr[-1]
                print(datetime_now, self.atr[vt_symbol], vt_symbol, open_d)
                # 根据日线数据的阴阳来更新次低价
                if close_d[-1] < open_d[-1]:
                    self.relative_min_price[vt_symbol].append(max(close_d[-1], low_d[-1]))
                else:
                    self.relative_min_price[vt_symbol].append(max(open_d[-1], low_d[-1]))

            # print(self.relative_max_price[vt_symbol])
            if len(self.relative_max_price[vt_symbol]) >= 13 and start_datetime <= datetime_now <= end_datetime:
                if datetime.date.today() == date_now:
                    self.close_all.append(close_m[-1])
                    self.datetime.append(datetime_now)
                    self.open_all.append(open_m[-1])
                    self.low_all.append(low_m[-1])
                    self.high_all.append(high_m[-1])
                    self.volume_all.append(volume_m[-1])
                # if self.is_trade and datetime_now == end_datetime:
                #     self.close = close_m[-1]
                #     close_data = {
                #         'Datetime': self.datetime,
                #         'Open': self.open_all,
                #         'High': self.high_all,
                #         'Low': self.low_all,
                #         'Close': self.close_all,
                #         'Volume': self.volume_all
                #     }
                #     # save_every_day_close(close_data, self.vt_symbol.split('-')[0])
                #     # save_open_close(self.open, self.close, self.pre_open, self.pre_close,
                #     #                 self.vt_symbol.split('-')[0])

                # print(self.pos[vt_symbol], vt_symbol)
                # 更新累计成交量
                if start_datetime == datetime_now:
                    self.accumulative_volume[vt_symbol] = 0
                # 三段
                if self.relative_max_price[vt_symbol][-1] < self.relative_max_price[vt_symbol][-2]:
                    self.buy_signal[vt_symbol]['three'] = 1
                    # print(datetime_now, 'three', self.buy_signal[vt_symbol]['three'])
                else:
                    self.buy_signal[vt_symbol]['three'] = 0
                # 四段
                if self.relative_max_price[vt_symbol][-1] < self.relative_max_price[vt_symbol][-2] < self.relative_max_price[vt_symbol][-3] or \
                        self.relative_max_price[vt_symbol][-2] < self.relative_max_price[vt_symbol][-1] < self.relative_max_price[vt_symbol][-3]:
                    self.buy_signal[vt_symbol]['four'] = 1
                    # print(datetime_now,'four', self.buy_signal[vt_symbol]['four'])
                else:
                    self.buy_signal[vt_symbol]['four'] = 0

                # 在盘中进行交易
                # 对成交量异常值进行检测，通过检查数量级来判断
                # 如果当前bar的成交量和前面两根bar相差>=三个数量级则为异常值
                # 加1防止定义域错误
                if int(log10(volume_m[-1] + 1)) - int(log10(volume_m[-2] + 1)) >= 3 and \
                        int(log10(volume_m[-1] + 1)) - int(log10(volume_m[-3] + 1)) >= 3:
                    self.accumulative_volume[vt_symbol] += int((volume_m[-1] - 1) / 100)
                else:
                    self.accumulative_volume[vt_symbol] += volume_m[-1]

                threshold = max(self.relative_max_price[vt_symbol][-1], self.relative_max_price[vt_symbol][-2])
                # 买入
                # print('price', bar.close_price, 'qiantian', self.relative_max_price[vt_symbol][-2], 'day_volume', volume_d[-1],
                #       'acc_volume', self.accumulative_volume[vt_symbol], )
                # print(bar.datetime, 'volume', volume_m[-1], volume_m[-2], 'atr', self.atr)

                # 写入log文件
                # log_data = f'time:{bar.datetime} price:{bar.close_price} prepre_day_relative_max_price:{self.relative_max_price[vt_symbol][-2]} ' \
                #            f'pre_day_volume:{volume_d[-1]} pre_min_bar_volume_m:{volume_m[-2]} volume_m_now:{volume_m[-1]} ' \
                #            f'acc_volume:{self.accumulative_volume[vt_symbol]} atr:{self.atr[vt_symbol]} pre_day_relative_min_price:{self.relative_min_price[vt_symbol][-1]}' \
                #            f'last_buy_date:{self.last_buy_date} buy_signal:{self.buy_signal[vt_symbol]} threshold:{threshold}' \
                #            f'close_m_now:{close_m[-1]} bar_close_m_now:{bar.close_price}\n'
                # save_log(vt_symbol, log_data)
                # position = Position(self.pos, 1000000, stock_limit=50)
                # size = position.calculate_position(close_m[-1])
                position = self.pos[vt_symbol]

                if self.buy_signal[vt_symbol]['three'] > 0 and close_m[-1] >= self.relative_max_price[vt_symbol][-2] and \
                        self.count[vt_symbol] == 1 and self.accumulative_volume[vt_symbol] > volume_d[-1] * self.volume_rate \
                        and position <= 0:
                    self.flag = True
                    stop_loss = self.relative_min_price[vt_symbol][-1] - self.atr_level * self.atr[vt_symbol]
                    stop_profit = self.relative_max_price[vt_symbol][-2] + self.atr_level * self.atr[vt_symbol]
                    data = {
                        'Symbol': vt_symbol.split('-')[0],
                        'Price': self.relative_max_price[vt_symbol][-2],
                        'Direction': 'buy',
                        'Size': self.fix_size,
                        'Position': position,
                        'stop_loss_range': stop_loss,
                        'stop_earning_range': stop_profit
                    }
                    # print(data)
                    # if data not in self.email_data.values():
                    #     self.email_data[time_str] = data
                    #     print(data)
                        # save_json(self.vt_symbol.split('-')[0], self.email_data)
                    # print(self.buy_signal[vt_symbol])
                    if self.last_buy_price[vt_symbol] != self.relative_max_price[vt_symbol][-2]:
                        self.last_buy_price[vt_symbol] = self.relative_max_price[vt_symbol][-2]
                        self.buy(vt_symbol, price=self.relative_max_price[vt_symbol][-2], volume=self.fix_size)
                        print(bar.datetime, self.buy_signal[vt_symbol], self.relative_max_price[vt_symbol][-2], vt_symbol, position)
                elif self.buy_signal[vt_symbol]['four'] > 0 and close_m[-1] >= threshold and \
                        self.count[vt_symbol] == 1 and \
                        self.accumulative_volume[vt_symbol] > volume_d[-1] * self.volume_rate and position <= 0:
                    self.flag = True
                    stop_loss = self.relative_min_price[vt_symbol][-1] - self.atr_level * self.atr[vt_symbol]
                    stop_profit = self.relative_max_price[vt_symbol][-2] + self.atr_level * self.atr[vt_symbol]
                    data = {
                        'Symbol': vt_symbol.split('-')[0],
                        'Price': self.relative_max_price[vt_symbol][-2],
                        'Direction': 'buy',
                        'Size': self.fix_size,
                        'Position': position,
                        'stop_loss_range': stop_loss,
                        'stop_earning_range': stop_profit
                    }
                    # print(data)
                    # if data not in self.email_data.values():
                    #     self.email_data[time_str] = data
                        # save_json(self.vt_symbol.split('-')[0], self.email_data)
                    if self.last_buy_price[vt_symbol] != self.relative_max_price[vt_symbol][-2]:
                        self.last_buy_price[vt_symbol] = self.relative_max_price[vt_symbol][-2]
                        self.buy(vt_symbol=vt_symbol, price=self.relative_max_price[vt_symbol][-2], volume=self.fix_size)
                        print(bar.datetime, self.buy_signal[vt_symbol],self.relative_max_price[vt_symbol][-2], vt_symbol, position)
                    # print(self.buy_signal)
                # ATR止损
                if close_m[-1] < self.relative_min_price[vt_symbol][-1] - self.atr_level * self.atr[vt_symbol] and position > 0:
                    price = self.relative_min_price[vt_symbol][-1] - self.atr_level * self.atr[vt_symbol]
                    data = {
                        'Symbol': vt_symbol.split('-')[0],
                        'Price': price,
                        'Direction': 'sell',
                        'Size': position,
                        'Position': 0
                    }
                    # print(data)
                    # if data not in self.email_data.values():
                    #     self.email_data[time_str] = data
                    #     save_json(self.vt_symbol.split('-')[0], self.email_data)
                    self.flag = False
                    if self.last_sell_price[vt_symbol] != price:
                        self.last_sell_price[vt_symbol] = price
                        self.sell(vt_symbol=vt_symbol, price=close_m[-1], volume=position, )
                        print(bar.datetime, close_m[-1], vt_symbol, position, self.atr[vt_symbol], self.relative_min_price[vt_symbol][-1])
                elif open_m[-1] < self.relative_min_price[vt_symbol][-1] - self.atr_level * self.atr[vt_symbol] and position > 0:
                    self.flag = False
                    price = self.relative_min_price[vt_symbol][-1] - self.atr_level * self.atr[vt_symbol]
                    data = {
                        'Symbol': vt_symbol.split('-')[0],
                        'Price': price,
                        'Direction': 'sell',
                        'Size': self.pos,
                        'Position': 0
                    }
                    # print(data)
                    # if data not in self.email_data.values():
                    #     self.email_data[time_str] = data
                    #     save_json(self.vt_symbol.split('-')[0], self.email_data)
                    if self.last_sell_price[vt_symbol] != price:
                        self.last_sell_price[vt_symbol] = price
                        self.sell(vt_symbol=vt_symbol, price=close_m[-1], volume=position)
                        print(bar.datetime, close_m[-1], vt_symbol, position, self.atr[vt_symbol], self.relative_min_price[vt_symbol][-1])

              
        self.put_event()

    def on_daily_bars(self, bars):
        # self.cancel_all()
        for vt_symbol, bar in bars.items():
            am_daily = self.am_dailys[vt_symbol]
            am_daily.update_bar(bar)

            # if not am_daily.inited:
            #     return

    def find_relative_max_price(self, open_d, close_d):
        if open_d > close_d:
            return open_d
        else:
            return close_d
