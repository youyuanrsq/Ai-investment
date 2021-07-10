from vnpy.app.script_trader import init_cli_trading
from vnpy.app.script_trader.cli import process_log_event
from vnpy.gateway.ib import IbGateway
from time import sleep
from datetime import datetime
from vnpy.trader.constant import Exchange
from vnpy.trader.object import SubscribeRequest
from vnpy.trader.object import HistoryRequest
from vnpy.trader.object import Interval
from vnpy.trader.database import database_manager
from pytz import timezone


def download_data(symbols, start, end):
    """
    start和end的时间格式为:20190101
    """
    # 连接IB
    setting = {
        "TWS地址": "127.0.0.1",
        "TWS端口": 7497,
        "客户号": 5,
        "交易账户": ""
    }
    engine = init_cli_trading([IbGateway])  # 返回Script_engine 示例，并且给main_engine注册了gateway
    # engine = BacktestingEngine([IbGateway])
    engine.connect_gateway(setting, "IB")  # 链接

    # 订阅
    for symbol in symbols:
        req1 = SubscribeRequest(symbol, Exchange.SMART)  # 创建行情订阅
        engine.main_engine.subscribe(req1, "IB")

    sleep(5)
    # 下载数据
    start = datetime.strptime(start, "%Y%m%d").replace(tzinfo=timezone('UTC'))
    end = datetime.strptime(end, "%Y%m%d").replace(tzinfo=timezone('UTC'))
    for symbol in symbols:
        historyreq = HistoryRequest(
            symbol=symbol,
            exchange=Exchange.SMART,
            start=start,
            end=end,
            interval=Interval.MINUTE
        )
        # # 读取历史数据，并把历史数据BarData放入数据库
        bardatalist = engine.main_engine.query_history(historyreq, "IB")

        database_manager.save_bar_data(bardatalist)
        print(symbol, '数据下载成功')
        sleep(5)


