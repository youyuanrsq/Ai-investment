import backtrader as bt
import os
import pandas as pd
import datetime
from portfolio_test_mod import ModStrategy


def from_local_read_company_name(filepath=''):
    filenames = os.listdir(filepath)
    company_names = []
    for filename in filenames:
        company = filename.split('.')[0]
        company_names.append(company)
    return company_names


def main(data_path, company_names):
    cerebro = bt.Cerebro(stdstats=False)


    for name in company_names:
        try:
          df = pd.read_csv(data_path+name+'.CSV', skiprows=0, header=0)
          df['Date'] = pd.to_datetime(df['Date'])
          data = bt.feeds.PandasData(
            dataname=df,
            datetime=0,  # 使用索引列作日期列
            open=1,  # 开盘价所在列
            high=2,  # 最高价所在列
            low=3,  # 最低价所在列
            close=4,  # 收盘价价所在列
            volume=5,  # 成交量所在列
            openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
            plot=False,
            fromdate=datetime.datetime(2016, 3, 14),
            todate=datetime.datetime(2021, 3, 12),
          )
          if len(df) > 300:
            cerebro.adddata(data)
        except Exception as e:
            print(e)

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addstrategy(ModStrategy)
    cerebro.broker.set_cash(1000000.)
    # cerebro.broker.set_coc(True)
    # 设置交易单位大小
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # 设置佣金为千分之一
    cerebro.broker.setcommission(commission=0.000)
    # cerebro.addwriter(bt.WriterFile, csv=True, out=modpath+'\\log\\test.csv', rounding=2)

    start_portfolio_value = cerebro.broker.get_value()

    results = cerebro.run()
    end_portfolio_value = cerebro.broker.get_value()
    pnl = end_portfolio_value - start_portfolio_value
    print('Starting Portfolio Value: %.2f' % start_portfolio_value)
    print('Final Portfolio Value: %.2f' % end_portfolio_value)
    print('PnL: %.2f' % pnl)

    sharpe_ratio = results[0].analyzers.sharperatio.get_analysis()['sharperatio']
    annual_return = results[0].analyzers.returns.get_analysis()['rnorm100']
    max_drawdown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
    print('max_drawdown:', max_drawdown)
    # for a in results[0].analyzers:
    #     a.print()


if __name__ == '__main__':
    # 输入的是存放不同指数股票的文件夹名称
    # main('SP_500')
    test_name = ['FUTU','GAN','AAPL']
    data_path = '../trading_data/day_data/'
    main(data_path, test_name)

# total_trade = results[0].analyzers.tradeanalyzer.get_analysis()['total']['closed']
# gross_pnl = results[0].analyzers.tradeanalyzer.get_analysis()['pnl']['gross']['total']
# won = results[0].analyzers.tradeanalyzer.get_analysis()['won']['total']
# won_rate = won / total_trade

# with open(modpath+'\\log\\baseline_ARKW_1y_turtle_position_management_voting_profit_taking.csv', 'w') as f:
# # with open(modpath + '\\log\\macd_with_stop_loss_and_position_control_spy_s.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(('sharpe_ratio', sharpe_ratio))
#     writer.writerow(('annual_return', annual_return))
#     writer.writerow(('max_drawdown', max_drawdown))
#     # writer.writerow(('total_trade', total_trade))
    # writer.writerow(('gross_pnl', gross_pnl))
    # writer.writerow(('won', won))
    # writer.writerow(('won_rate', won_rate))

#

# cerebro.plot()
# for a in results[0].analyzers:
#     a.print()
