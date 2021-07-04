from datetime import datetime
from importlib import reload
from vnpy.app.portfolio_strategy import BacktestingEngine
from vnpy.trader.constant import Interval
from vnpy.app.portfolio_strategy.strategies import multi_timeframe_portfolio_strategy

'''
该文件应在 portfolio_streategy下
'''

def set_ratios(num, vt_symbols):
    """
    设置每个vt_symbol的回测参数，最终返回字典格式
    用于设置手续费，滑点，合约规模，price tick
    """
    d = {}
    for i in vt_symbols:
        d[i] = num
    return d


def show_result(
        vt_symbols,
        strategy,
        setting={},
        show_chart=True
):
    # 1)创建回测引擎
    engine = BacktestingEngine()

    # 2）设置回测参数
    engine.set_parameters(
        vt_symbols=vt_symbols,
        #         interval=Interval.DAILY,
        interval=Interval.MINUTE,
        start=datetime(2019, 9, 1),
        end=datetime(2021, 3, 31),
        rates=set_ratios(1 / 10000, vt_symbols),
        slippages=set_ratios(0, vt_symbols),
        sizes=set_ratios(1, vt_symbols),
        priceticks=set_ratios(0.01, vt_symbols),
        capital=5_000_000,
    )

    # 3)添加策略
    engine.add_strategy(strategy, setting)
    # 4) 加载历史数据
    engine.load_data()
    # 5) 跑回测，基于事件引擎逐条回放，得到成交记录
    engine.run_backtesting()
    # 6) 基于逐日顶市规则和成交记录，得到组合资金曲线
    df = engine.calculate_result()
    # 7) 基于资金曲线，计算策略回测指标，如收益率，夏普比率
    engine.calculate_statistics()
    # 8) 画图
    if show_chart:
        engine.show_chart()


show_result(["AAWW-USD-STK.SMART", "SID-USD-STK.SMART"], multi_timeframe_portfolio_strategy.MultiTimeframePortfolioStrategy)

