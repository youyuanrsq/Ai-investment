import talib
from talib import MA_Type
import pandas as pd
import datetime
import os
import numpy as np
import warnings
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
warnings.filterwarnings("ignore")


def price_corr(df, A, B, extra_dict={'period': [5, 10, 20], 'is_direction': True}):
    """
    :param df:  股票的历史交易信息，需要包含A,B两个序列的数据
    :param A :  股票的价格，一般为Close
    :param B :  可以是成交量Volume或者其他指标
    :param extra_dict :  额外的参数，这个字典可以传入周期period，以及是否要判断股票的在周期的方向
    :return: df ，df包含有不同周期的相关系数，以及股票此时的方向
    """
    price = df[A]
    factor = df[B]
    period = extra_dict['period']
    # 这个是用来判断股价的方向，如果当天比前n天高，为+1，低为-1
    direction = extra_dict['is_direction']
    for n in period:
        if direction:
            df['direction_%d' % n] = (df['Close'] - df['Close'].shift(n)) / abs(df['Close'] - df['Close'].shift(n))
            # 这个factor 滚不滚动都是取n个周期
            df['{}_corr_{}'.format(B, n)] = price.rolling(n).corr(factor)

            # 进阶版相关系数
            df['{}_corr_{}'.format(B, n)] = np.where(
                ((df['direction_%d' % n] == -1.0) & (df['{}_corr_{}'.format(B, n)] < 0))
                , df['{}_corr_{}'.format(B, n)], df['{}_corr_{}'.format(B, n)] * df['direction_%d' % n])

        else:
            df['{}_corr_{}'.format(B, n)] = price.rolling(n).corr(factor)
    return df

# 测试因子的一个胜率
def test_beili(df, period=[5, 10, 20]):
    period0 = period
    for i in range(0, 50, 2):
        i = i / 50
        for n in period0:
            # 给出交易信号,当相关系数>i的时候确定为做多信号，进行买入
            df['trade_type_%d' % n] = np.where(
                (df['{}_corr_{}'.format(B, n)] > i)
                , 1, 0)
            # 计算n天后的涨跌幅
            df['pct_chg_%d' % n] = 100 * (df['Close'].shift(-1 * n) / df['Close'] - 1)

        # 计算胜率
        for n in period0:
            # 总给出做多信号的次数
            sum_up = len(df[(df['trade_type_%d' % n] == 1)])
            print('{} Daily periodic correlation，when correlation >{} give the Rising-signal total data:{}'.format(n, i, sum_up))
            # 如果信号量不为0，则计算胜率
            if sum_up != 0:
                for j in period0:
                    # 筛选出 在给多信号的同时，且后n天的涨幅大于0的数量
                    buy_up = len(df[((df['trade_type_%d' % n] == 1) & (df['pct_chg_%d' % j] > 0))])
                    print('when give the Rising-signal data quantity，The probability of rising after{} days:{}'.format(j, buy_up / sum_up))
                print('\n')


if __name__ == '__main__':
    df = pd.read_csv('./AAPL.CSV', encoding='GBK')
    extra_dict = {'period': [5, 10, 20], 'is_direction': False}
    A = 'Close'
    B = 'Volume'
    # 如果B为MACD时，需要利用Talib计算MACD指标
    # df['DIF'], df['DEA'], df['MACD'] = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df = price_corr(df, A, B, extra_dict)

    test_beili(df)

