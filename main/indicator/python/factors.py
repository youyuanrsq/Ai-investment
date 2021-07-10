import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import os
import talib
from talib import MA_Type
import warnings

warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

# 显示中文
# plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 计算股票斜率代码
def slope_alpha21(df, period=6):
    data = df.copy()
    data['mean_%s' % period] = data['Close'].rolling(period).mean()
    data['slope21_%s' % period] = data['mean_%s' % period].rolling(period).apply(
        lambda x: np.polyfit(list(range(1, period + 1)), x.tolist(), deg=1)[0])
    del data['mean_%s' % period]
    return data['slope21_%s' % period]


# 计算乘离率
def bias(df, period=20):
    data = df.copy()
    data['mean_%s' % period] = data['Close'].rolling(period).mean()
    data['bias_%s' % period] = 100 * ((data['Close'] - data['mean_%s' % period]) / data['mean_%s' % period])
    return data['bias_%s' % period]


# 相关系数（A,B）
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


# 计算MACD与价格的相关性
def MACD_price_corr(df):
    data = df.copy()
    close_p = data['Close'].values
    data["DIF"], data["DEA"], data["MACD"] = talib.MACD(close_p, fastperiod=12, slowperiod=26,
                                                        signalperiod=9)
    A = 'Close'
    B = "DEA"
    data = price_corr(data, A='Close', B="DEA", extra_dict={'period': [5, 10, 20], 'is_direction': True})
    return data['{}_corr_{}'.format(B, 10)]


# 额外的指标
def extra_indicator(df, extra_agg_dict):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    # extra_agg_dict = {}
    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["CCI"] = talib.CCI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["CCI"] = 'last'

    df["TRIX"] = talib.TRIX(close_p, timeperiod=30)
    extra_agg_dict["TRIX"] = 'last'

    df["MINUS_DI"] = talib.MINUS_DI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["MINUS_DI"] = 'last'

    # df['slope21'] = slope_alpha21(df, period=6)
    # extra_agg_dict["slope21"] = 'last'
    #
    # df['bias'] = bias(df, period=20)
    # extra_agg_dict["bias"] = 'last'
    #
    # # =计算量价相关因子
    # df['vol_price_corr'] = df['Close'].rolling(5).corr(df['Volume'])
    # extra_agg_dict['vol_price_corr'] = 'last'
    #
    # # MACD与股价的相关系数
    # df['MACD_price_corr'] = MACD_price_corr(df)
    # extra_agg_dict['MACD_price_corr'] = 'last'

    return df, extra_agg_dict


# 获取talib的全部动量指标
def Momentum_Indicator(df, extra_agg_dict):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    # extra_agg_dict = {}
    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["ADX"] = talib.ADX(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["ADX"] = 'last'

    df["ADXR"] = talib.ADXR(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["ADXR"] = 'last'

    df["APO"] = talib.APO(close_p, fastperiod=12, slowperiod=26, matype=0)
    extra_agg_dict["APO"] = 'last'

    df["AROON_aroondown"], df["AROON_aroonup"] = talib.AROON(high_p, low_p, timeperiod=14)
    extra_agg_dict["AROON_aroondown"] = 'last'
    extra_agg_dict["AROON_aroonup"] = 'last'

    df["AROONOSC"] = talib.AROONOSC(high_p, low_p, timeperiod=14)
    extra_agg_dict["AROONOSC"] = 'last'

    df["BOP"] = talib.BOP(open_p, high_p, low_p, close_p)
    extra_agg_dict["BOP"] = 'last'

    df["CCI"] = talib.CCI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["CCI"] = 'last'

    df["CMO"] = talib.CMO(close_p, timeperiod=14)
    extra_agg_dict["CMO"] = 'last'

    df["DX"] = talib.DX(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["DX"] = 'last'

    df["MACD_macd"], df["MACD_macdsignal"], df["MACD_macdhist"] = talib.MACD(close_p, fastperiod=12, slowperiod=26,
                                                                             signalperiod=9)
    extra_agg_dict["MACD_macdhist"] = 'last'
    df["MACDEXT_macd"], df["MACDEXT_macdsignal"], df["MACDEXT_macdhist"] = talib.MACDEXT(close_p, fastperiod=12,
                                                                                         fastmatype=0, slowperiod=26,
                                                                                         slowmatype=0, signalperiod=9,
                                                                                         signalmatype=0)
    extra_agg_dict["MACDEXT_macdhist"] = 'last'

    df["MACDFIX_macd"], df["MACDFIX_macdsignal"], df["MACDFIX_macdhist"] = talib.MACDFIX(close_p, signalperiod=9)

    extra_agg_dict["MACDFIX_macdhist"] = 'last'

    df["MFI"] = talib.MFI(high_p, low_p, close_p, volume_p, timeperiod=14)
    extra_agg_dict["MFI"] = 'last'

    df["MINUS_DI"] = talib.MINUS_DI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["MINUS_DI"] = 'last'

    df["MINUS_DM"] = talib.MINUS_DM(high_p, low_p, timeperiod=14)
    extra_agg_dict["MINUS_DM"] = 'last'

    df["MOM"] = talib.MOM(close_p, timeperiod=10)
    extra_agg_dict["MOM"] = 'last'

    df["PLUS_DI"] = talib.PLUS_DI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["PLUS_DI"] = 'last'

    df["PLUS_DM"] = talib.PLUS_DM(high_p, low_p, timeperiod=14)
    extra_agg_dict["PLUS_DM"] = 'last'

    df["PPO"] = talib.PPO(close_p, fastperiod=12, slowperiod=26, matype=0)
    extra_agg_dict["PPO"] = 'last'

    df["ROC"] = talib.ROC(close_p, timeperiod=10)
    extra_agg_dict["ROC"] = 'last'

    df["ROCP"] = talib.ROCP(close_p, timeperiod=10)
    extra_agg_dict["ROCP"] = 'last'

    df["ROCR"] = talib.ROCR(close_p, timeperiod=10)
    extra_agg_dict["ROCR"] = 'last'

    df["RSI"] = talib.RSI(close_p, timeperiod=14)
    extra_agg_dict["RSI"] = 'last'

    df["STOCH_slowk"], df["STOCH_slowd"] = talib.STOCH(high_p, low_p, close_p, fastk_period=5, slowk_period=3,
                                                       slowk_matype=0, slowd_period=3, slowd_matype=0)
    extra_agg_dict["STOCH_slowk"] = 'last'

    df["STOCHF_fastk"], df["STOCHF_fastd"] = talib.STOCHF(high_p, low_p, close_p, fastk_period=5, fastd_period=3,
                                                          fastd_matype=0)
    extra_agg_dict["STOCHF_fastk"] = 'last'

    df["TRIX"] = talib.TRIX(close_p, timeperiod=30)
    extra_agg_dict["TRIX"] = 'last'

    df["ULTOSC"] = talib.ULTOSC(high_p, low_p, close_p, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    extra_agg_dict["ULTOSC"] = 'last'

    df["WILLR"] = talib.WILLR(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["WILLR"] = 'last'

    return df, extra_agg_dict


# Overlap Studies Functions 重叠研究指标
def Overlap_Studies(df):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values

    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["BBANDS_upper"], df["BBANDS_middle"], df["BBANDS_lower"] = talib.BBANDS(close_p, matype=MA_Type.T3)

    df["DEMA"] = talib.DEMA(close_p, timeperiod=30)

    df["MA"] = talib.MA(close_p, timeperiod=30, matype=0)

    df['EMA12'] = talib.EMA(np.array(close_p), timeperiod=6)

    df['EMA26'] = talib.EMA(np.array(close_p), timeperiod=12)

    df["KAMA"] = talib.KAMA(close_p, timeperiod=30)

    df['SMA'] = talib.SMA(close_p, timeperiod=30)

    df["MIDPOINT"] = talib.MIDPOINT(close_p, timeperiod=14)

    df["SAR"] = talib.SAR(high_p, low_p, acceleration=0, maximum=0)

    df["T3"] = talib.T3(close_p, timeperiod=5, vfactor=0)

    df["TEMA"] = talib.TEMA(close_p, timeperiod=30)

    df["MIDPRICE"] = talib.MIDPRICE(high_p, low_p, timeperiod=14)

    df["TRIMA"] = talib.TRIMA(close_p, timeperiod=30)

    df["SAREXT"] = talib.SAREXT(high_p, low_p, startvalue=0, offsetonreverse=0, accelerationinitlong=0,
                                accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0,
                                accelerationmaxshort=0)

    df["WMA"] = talib.WMA(close_p, timeperiod=30)

    return df

# 获取Volume Indicators 成交量指标
def Volume_Indicators(df, extra_agg_dict):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    volume = df["Volume"].values

    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["AD"] = talib.AD(high_p, low_p, close_p, volume_p)
    extra_agg_dict["AD"] = 'last'

    df["ADOSC"] = talib.ADOSC(high_p, low_p, close_p, volume_p, fastperiod=3, slowperiod=10)
    extra_agg_dict["ADOSC"] = 'last'

    df["OBV"] = talib.OBV(close_p, volume_p)
    extra_agg_dict["OBV"] = 'last'

    return df, extra_agg_dict


# Volatility Indicator Functions 波动率指标函数
def Volatility_Indicator(df, extra_agg_dict):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    volume = df["Volume"].values

    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["ATR"] = talib.ATR(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["ATR"] = 'last'

    df["NATR"] = talib.NATR(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["NATR"] = 'last'

    df["TRANGE"] = talib.TRANGE(high_p, low_p, close_p)
    extra_agg_dict["TRANGE"] = 'last'


    return df, extra_agg_dict


# Cycle Indicator Functions
# 周期指标
def Cycle_Indicator(df, extra_agg_dict):
    # Cycle Indicator Functions
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    volume = df["Volume"].values

    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["HT_DCPERIOD"] = talib.HT_DCPERIOD(close_p)
    extra_agg_dict["HT_DCPERIOD"] = 'last'

    df["HT_DCPHASE"] = talib.HT_DCPHASE(close_p)
    extra_agg_dict["HT_DCPHASE"] = 'last'

    df["HT_PHASOR_inphase"], df["HT_PHASOR_quadrature"] = talib.HT_PHASOR(close_p)
    extra_agg_dict["HT_PHASOR_inphase"] = 'last'
    extra_agg_dict["HT_PHASOR_quadrature"] = 'last'

    df["HT_SINE_sine"], df["HT_SINE_leadsine"] = talib.HT_SINE(close_p)
    extra_agg_dict["HT_SINE_sine"] = 'last'
    extra_agg_dict["HT_SINE_leadsine"] = 'last'

    df["HT_TRENDMODE"] = talib.HT_TRENDMODE(close_p)
    extra_agg_dict["HT_TRENDMODE"] = 'last'

    return df, extra_agg_dict


# Statistic Functions 统计学指标
def Statistic_Functions(df, extra_agg_dict):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    volume = df["Volume"].values

    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["BETA"] = talib.BETA(high_p, low_p, timeperiod=5)
    extra_agg_dict["BETA"] = 'last'

    df["CORREL"] = talib.CORREL(high_p, low_p, timeperiod=30)
    extra_agg_dict["CORREL"] = 'last'

    df["LINEARREG"] = talib.LINEARREG(close_p, timeperiod=14)
    extra_agg_dict["LINEARREG"] = 'last'

    df["LINEARREG_ANGLE"] = talib.LINEARREG_ANGLE(close_p, timeperiod=14)
    extra_agg_dict["LINEARREG_ANGLE"] = 'last'

    df["LINEARREG_INTERCEPT"] = talib.LINEARREG_INTERCEPT(close_p, timeperiod=14)
    extra_agg_dict["LINEARREG_INTERCEPT"] = 'last'

    df["LINEARREG_SLOPE"] = talib.LINEARREG_SLOPE(close_p, timeperiod=14)
    extra_agg_dict["LINEARREG_SLOPE"] = 'last'

    df["STDDEV"] = talib.STDDEV(close_p, timeperiod=5, nbdev=1)
    extra_agg_dict["STDDEV"] = 'last'

    df["TSF"] = talib.TSF(close_p, timeperiod=14)
    extra_agg_dict["TSF"] = 'last'

    df["VAR"] = talib.VAR(close_p, timeperiod=5, nbdev=1)
    extra_agg_dict["VAR"] = 'last'

    return df, extra_agg_dict


# 只计算有效指标
def Postive_Functions(df, extra_agg_dict):
    open_p = df['Open'].values
    high_p = df['High'].values
    close_p = df['Close'].values
    low_p = df['Low'].values
    volume = df["Volume"].values

    float_data = [float(x) for x in df["Volume"].values]
    volume_p = np.array(float_data)

    df["CCI"] = talib.CCI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["CCI"] = 'last'

    # df["LINEARREG_ANGLE"] = talib.LINEARREG_ANGLE(close_p, timeperiod=14)
    # extra_agg_dict["LINEARREG_ANGLE"] = 'last'

    df["AD"] = talib.AD(high_p, low_p, close_p, volume_p)
    extra_agg_dict["AD"] = 'last'

    # df["ATR"] = talib.ATR(high_p, low_p, close_p, timeperiod=14)
    # extra_agg_dict["ATR"] = 'last'

    # df["NATR"] = talib.NATR(high_p, low_p, close_p, timeperiod=14)
    # extra_agg_dict["NATR"] = 'last'

    df["MINUS_DI"] = talib.MINUS_DI(high_p, low_p, close_p, timeperiod=14)
    extra_agg_dict["MINUS_DI"] = 'last'

    df["TRIX"] = talib.TRIX(close_p, timeperiod=30)
    extra_agg_dict["TRIX"] = 'last'

    return df, extra_agg_dict