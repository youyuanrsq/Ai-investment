#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd
import os
import peakutils
import numpy as np
import talib
from talib import MA_Type
import pandas as pd
import datetime
import os
from urllib.request import urlopen
import json
import itertools
import scipy
from numpy import inf
from scipy.stats import norm
import pyecharts.options as opts
from pyecharts.charts import Candlestick, Line
import random
import json


# In[22]:


# 获取talib的全部动量指标
class Index:
    def __init__(self):
        self.index_list = ["ADX, ADXR", "APO", "AROON_aroondown", "AROONOSC", "BOP", "CCI",
                           "CMO", "DX", "MACD_macd", "MACDEXT_macd", "MACDFIX_macd", "MFI",
                           "MINUS_DI", "MINUS_DM", "MOM", "PLUS_DI", "PLUS_DM", "PPO", "ROC",
                           "ROCP", "ROCR", "RSI", "STOCH", "STOCHF", "TRIX", "ULTOSC", "WILLR", "VIXFIX"]

    def Momentum_Indicator(self, df, indicator):
        """
        df: dataframe, 股票数据
        indicator: str, 指标
        """
        open_p = df['open'].values
        high_p = df['high'].values
        close_p = df['close'].values
        low_p = df['low'].values
        volume = df["volume"].values
        volume_p = df["volume"].values

        float_data = [float(x) for x in df["volume"].values]
        volume_p = np.array(float_data)
        if indicator == "ADX":
            df["ADX"] = talib.ADX(high_p, low_p, close_p, timeperiod=14)

        if indicator == "ADXR":
            df["ADXR"] = talib.ADXR(high_p, low_p, close_p, timeperiod=14)

        if indicator == "APO":
            df["APO"] = talib.APO(close_p, fastperiod=12, slowperiod=26, matype=0)

        if indicator == "AROON_aroondown":
            df["AROON_aroondown"], df["AROON_aroonup"] = talib.AROON(high_p, low_p, timeperiod=14)

        if indicator == "AROONOSC":
            df["AROONOSC"] = talib.AROONOSC(high_p, low_p, timeperiod=14)

        if indicator == "BOP":
            df["BOP"] = talib.BOP(open_p, high_p, low_p, close_p)

        if indicator == "CCI":
            df["CCI"] = talib.CCI(high_p, low_p, close_p, timeperiod=14)

        if indicator == "CMO":
            df["CMO"] = talib.CMO(close_p, timeperiod=14)

        if indicator == "DX":
            df["DX"] = talib.DX(high_p, low_p, close_p, timeperiod=14)

        if indicator == "MACD_macd":
            df["MACD_macd"], df["MACD_macdsignal"], df["MACD_macdhist"] = talib.MACD(close_p, fastperiod=12,
                                                                                     slowperiod=26, signalperiod=9)

        if indicator == "MACDEXT_macd":
            df["MACDEXT_macd"], df["MACDEXT_macdsignal"], df["MACDEXT_macdhist"] = talib.MACDEXT(close_p, fastperiod=12,
                                                                                                 fastmatype=0,
                                                                                                 slowperiod=26,
                                                                                                 slowmatype=0,
                                                                                                 signalperiod=9,
                                                                                                 signalmatype=0)

        if indicator == "MACDFIX_macd":
            df["MACDEXT_macd"], df["MACDEXT_macdsignal"], df["MACDEXT_macdhist"] = talib.MACDEXT(close_p, fastperiod=12,
                                                                                                 fastmatype=0,
                                                                                                 slowperiod=26,
                                                                                                 slowmatype=0,
                                                                                                 signalperiod=9,
                                                                                                 signalmatype=0)

        if indicator == "MFI":
            df["MFI"] = talib.MFI(high_p, low_p, close_p, volume_p, timeperiod=14)

        if indicator == "MINUS_DI":
            df["MINUS_DI"] = talib.MINUS_DI(high_p, low_p, close_p, timeperiod=14)

        if indicator == "MINUS_DM":
            df["MINUS_DM"] = talib.MINUS_DM(high_p, low_p, timeperiod=14)

        if indicator == "MOM":
            df["MOM"] = talib.MOM(close_p, timeperiod=10)

        if indicator == "PLUS_DI":
            df["PLUS_DI"] = talib.PLUS_DI(high_p, low_p, close_p, timeperiod=14)

        if indicator == "PLUS_DM":
            df["PLUS_DM"] = talib.PLUS_DM(high_p, low_p, timeperiod=14)

        if indicator == "PPO":
            df["PPO"] = talib.PPO(close_p, fastperiod=12, slowperiod=26, matype=0)

        if indicator == "ROC":
            df["ROC"] = talib.ROC(close_p, timeperiod=10)

        if indicator == "ROCP":
            df["ROCP"] = talib.ROCP(close_p, timeperiod=10)

        if indicator == "ROCR":
            df["ROCR"] = talib.ROCR(close_p, timeperiod=10)

        if indicator == "RSI":
            df["RSI"] = talib.RSI(close_p, timeperiod=14)

        if indicator == "STOCH":
            df["STOCH_slowk"], df["STOCH_slowd"] = talib.STOCH(high_p, low_p, close_p, fastk_period=5, slowk_period=3,
                                                               slowk_matype=0, slowd_period=3, slowd_matype=0)

        if indicator == "STOCHF":
            df["STOCHF_fastk"], df["STOCHF_fastd"] = talib.STOCHF(high_p, low_p, close_p, fastk_period=5,
                                                                  fastd_period=3, fastd_matype=0)

        if indicator == "TRIX":
            df["TRIX"] = talib.TRIX(close_p, timeperiod=30)

        if indicator == "ULTOSC":
            df["ULTOSC"] = talib.ULTOSC(high_p, low_p, close_p, timeperiod1=7, timeperiod2=14, timeperiod3=28)
        if indicator == "WILLR":
            df["WILLR"] = talib.WILLR(high_p, low_p, close_p, timeperiod=14)
        if indicator == "VIXFIX":
            df["VIXFIX"] = self.VIXFIX(df)
       # df = df.drop(range(35))
        return self.normalise(df, indicator)

    def normalise(self, data, indicator):
        """
        标准化每一个指标
        """
        for column in data.columns:
            if indicator in column:
                df = data[~np.isnan(data[column])]
                df = df[~np.isinf(df[column])][column]
                avg, std = norm.fit(df)
                norm_list = []
                for i in range(data.shape[0]):
                    if np.isnan(data[column][i]):
                        norm_list.append(0)
                    else:
                        zscore = (data[column][i] - avg) / std
                        norm_list.append(norm.cdf(zscore) * 100)
                # 标准化
                norm_indicator = column + "_NORM"
                data[norm_indicator] = norm_list
        return data

    def VIXFIX(self, data):
        """
        Function is to calculate vixfix index based on the input data.
        """
        if "close" not in data.columns:
            return data

        def HHV(data, N):
            data["HHV"] = data.close.rolling(N).max().shift()
            data = data.fillna(0)
            return data

        data = HHV(data, N=21)
        # VIXFIX 未标准化
        return 100 * (data["HHV"] - data["low"]) / data["HHV"]

    # In[23]:


def test(transform_df, time_period, index):
    """
    parameters:
    indicator: str
    time_period: int, 回测天数
    buy_thredhold: 列表, 记录买入阈值
    sell_threshold: 列表, 记录卖出阈值
    """
    # 输入测试数据
    buy_y_rate = {}
    sell_y_rate = {}

    buy_high_signal_total = 0
    buy_high_y = 0
    buy_high_n = 0
    sell_high_signal_total = 0
    sell_high_y = 0
    sell_high_n = 0

    buy_low_signal_total = 0
    buy_low_y = 0
    buy_low_n = 0
    sell_low_signal_total = 0
    sell_low_y = 0
    sell_low_n = 0



    signalindex = np.where(transform_df[index + '_buyHigh'])[0]
    for i in signalindex:
            current = transform_df.iloc[i]
            future = transform_df.iloc[i+1: i+ 1+ time_period]
            if current[index +'_buyHigh'] :
                buy_high_signal_total += 1
                if (future["close"].max() - current["close"]) > 0:
                    # 买入信号有效
                    buy_high_y += 1
                else:
                    buy_high_n += 1
    signalindex = np.where(transform_df[index + '_buyLow'])[0]
    for i in signalindex:
            current = transform_df.iloc[i]
            future = transform_df.iloc[i + 1: i + 1 + time_period]
            if current[index + '_buyLow']:
                buy_low_signal_total += 1
                if (future["close"].max() - current["close"])  > 0:
                    # 买入信号有效
                    buy_low_y += 1
                else:
                    buy_low_n += 1
    signalindex = np.where(transform_df[index + '_sellHigh'])[0]
    for i in signalindex:
            current = transform_df.iloc[i]
            future = transform_df.iloc[i + 1: i + 1 + time_period]
            if current[index + '_sellHigh']:
                sell_high_signal_total += 1
                if (future["close"].min() - current["close"])  < 0:
                    # 买入信号有效
                    sell_high_y += 1
                else:
                    sell_high_n += 1
    signalindex = np.where(transform_df[index + '_sellLow'])[0]
    for i in signalindex:
            current = transform_df.iloc[i]
            future = transform_df.iloc[i + 1: i + 1 + time_period]
            if current[index + '_sellLow']:
                sell_low_signal_total += 1
                if (future["close"].min() - current["close"]) < 0:
                    # 买入信号有效
                    sell_low_y += 1
                else:
                    sell_low_n += 1



    if buy_high_signal_total != 0:
                stock_buy_high_y_rate = buy_high_y / buy_high_signal_total
    else:
                stock_buy_high_y_rate = 0
    if sell_high_signal_total != 0:
               stock_sell_high_y_rate = sell_high_y / sell_high_signal_total
    else:
                stock_sell_high_y_rate = 0

    if buy_low_signal_total != 0:
                stock_buy_low_y_rate = buy_low_y / buy_low_signal_total
    else:
                stock_buy_low_y_rate = 0
    if sell_low_signal_total != 0:
                stock_sell_low_y_rate = sell_low_y / sell_low_signal_total
    else:
                stock_sell_low_y_rate = 0
    print('stock_buy_high_y_rate', stock_buy_high_y_rate,
         'stock_sell_high_y_rate, ',stock_sell_high_y_rate,
         'stock_buy_low_y_rate,',stock_buy_low_y_rate,
         'stock_sell_low_y_rate',stock_sell_low_y_rate)
    return stock_buy_high_y_rate, stock_sell_high_y_rate, stock_buy_low_y_rate,stock_sell_low_y_rate

def save_to_json(dic, filename):
    newdict = {}
    for day, value in dic.items():
        value_str = {}
        for threshold_comb, rate in value.items():
            value_str[str(threshold_comb)] = rate
        newdict[str(day)] = value_str
    with open(filename + ".json", "w+") as f:
        json.dump(newdict, f)


# In[25]:


def give_signal(df, buy_threshold, sell_threshold):
    index_columns = [a for a in df.columns if "NORM" in a]
    for i in index_columns:
        print(i)

        for index, z in enumerate(df[i]):
            if z < 4:
                df[i][index] = 4
        df[i] = peakutils.prepare.scale(df[i], new_range=(0, 100), eps=1e-09)[0]
        df[i+'_buyHigh'] =  df[i] > buy_threshold
        df[i+'_buyLow'] =  df[i] <= buy_threshold
        df[i+'_sellHigh'] =  df[i] > sell_threshold
        df[i+'_sellLow'] =  df[i] <= sell_threshold
    return df


# In[26]:


def main(indicator, data_path):
    """
    indicator: str 测试指标名字
    threshold_parameters: 列表, [buy_threshold, sell_threshold]
    """
    # 导入测试文件路径
    filenames = os.listdir(data_path)
    # 随机选择测试文件
    random.shuffle(filenames)
    testfiles = filenames
    days = [x for x in range(2, 6)]
    buy_thresholds = [x for x in range(5, 20)]  + [x for x in range(75, 90)]
    sell_thresholds =[x for x in range(75, 90)] + [x for x in range(5, 20)]
    buy_y_day = {}
    sell_y_day = {}

    import csv

    idtest=  open('id_test.csv', mode='w')
    if 1:
      idcsv = csv.writer(idtest, delimiter=',')

      idcsv.writerow(['stock', 'id', 'day','buy_threshold', 'sell_threshold', 'buy_high_y_rate', 'sell_high_y_rate','buy_low_y_rate', 'sell_low_y_rate' ])

      for file in testfiles:
        print(file)
        stock_name = file[0: file.index(".")]
        print('stock', stock_name)
       # if stock_name != 'FUBO':
        #    continue
        path = data_path + file
        # 给出信号
        # try:
        if 1:
            df = pd.read_csv(path, skiprows=[i for i in range(1,35)] )
            comb_threshold = list(itertools.product(buy_thresholds, sell_thresholds))
            index_columns = [a for a in df.columns if "NORM" in a]
            for buy_threshold, sell_threshold in comb_threshold:
                # try:
                    print(buy_threshold, sell_threshold)
                    transform_df = give_signal(df.copy(), buy_threshold, sell_threshold)
                    for day in days:
                        print('day', day)
                        for index in index_columns:
                            buy_high_y_rate, sell_high_y_rate, buy_low_y_rate, sell_low_y_rate = test(transform_df,  day,index)
                            buy_y_day[stock_name] = [day, index, buy_high_y_rate, sell_high_y_rate, buy_low_y_rate, sell_low_y_rate ]
                            ss = [stock_name, index, day, buy_threshold, sell_threshold, buy_high_y_rate, sell_high_y_rate,
                                  buy_low_y_rate, sell_low_y_rate]
                            idcsv.writerow( [i for i in ss ] )
                # except Exception as e:
                #     print(e)
        # except Exception as e:
        #     print(e)
    # save_to_json(buy_y_day, indicator + "-buy")
    # save_to_json(sell_y_day, indicator + "-sell")
    # buy_points = transform_to_point(buy_y_day, "buy")
    # sell_points = transform_to_point(sell_y_day, "sell")
    # plot(buy_points, "buy", indicator)
    # plot(sell_points, "sell", indicator)
    #return


# In[27]:


from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.pyplot import figure


def plot(points, direction, indicator):
    """
    points: 数据点
    direction: buy or sell
    """
    #     max_index = np.argmax(value)
    #     day_max = days[max_index]
    #     buy_th_max = buy_th[max_index]
    #     sell_th_max = sell_th[max_index]
    #     value_max = value[max_index]
    days = [x[0] for x in points]
    th = [x[1] for x in points]
    value = [x[2] for x in points]
    max_index = np.argmax(value)
    min_index = np.argmin(value)
    point_max = points[max_index]
    point_min = points[min_index]

    fig = plt.figure()
    plt.rcParams["figure.figsize"] = (30, 30)
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter3D(days, th, value)
    ax.set_xlabel('day')  # 坐标轴
    ylabel = "{}_th".format(direction)
    ax.set_ylabel(ylabel)
    ax.set_zlabel('successful rate')
    ax.text(point_max[0], point_max[1], round(point_max[2], 3),
            "max:\n (day={}, {}={}, rate={}".format(point_max[0], ylabel, point_max[1], round(point_max[2], 3)),
            size=14, ha='center', va='center')
    ax.text(point_min[0], point_min[1], round(point_min[2], 3),
            "min:\n (day={}, {}={}, rate={}".format(point_min[0], ylabel, point_min[1], round(point_min[2], 3)),
            size=14, ha='center', va='baseline')
    fig.tight_layout()
    plt.show()
    fig.savefig('{}-{}.png'.format(indicator, direction), dpi=100, bbox_inches='tight')


# In[28]:


def transform_to_point(dic, direction):
    """
    dic: 字典
    direction: buy or sell
    """
    points = []
    days = dic.keys()
    all_thresholds = list(dic[1].keys())
    for day in days:
        for buy_th, sell_th in all_thresholds:
            value = dic[day][(buy_th, sell_th)]
            if direction == "buy":
                points.append((day, buy_th, value))
            elif direction == "sell":
                points.append((day, sell_th, value))
    return list(set(points))


# In[30]:


if __name__ == "__main__":
    data_path = "/home/zhubo/Desktop/trading_data/all/day_id/"
    indicator = "VIXFIX"
    print(indicator)
    main(indicator, data_path)

# In[ ]:

