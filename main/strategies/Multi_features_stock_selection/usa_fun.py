from factors import *
from alpha101 import *

warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

# 显示中文
# plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_index_data(index_path, start_date, end_date):
    index_data = pd.read_csv(index_path, encoding='GBK')
    index_data = index_data[(index_data['Date'] >= start_date) & (index_data['Date'] <= end_date)]
    index_data.reset_index(drop=True, inplace=True)
    index_data = index_data[['Date']]
    return index_data


# 将股票数据和指数数据合并
def merge_with_index_data(df, index_data, extra_fill_0_list=[]):
    """
    原始股票数据在不交易的时候没有数据。
    将原始股票数据和指数数据合并，可以补全原始股票数据没有交易的日期。
    :param df: 股票数据
    :param index_data: 指数数据
    :return:
    """
    # ===将股票数据和指数合并，结果已经排序
    df = pd.merge(left=df, right=index_data, on='Date', how='right', sort=True, indicator=True)
    # ===对开、高、收、低、前收盘价价格进行补全处理
    # 用前一天的收盘价，补全收盘价的空值
    df['Close'].fillna(method='ffill', inplace=True)
    # 用收盘价补全开盘价、最高价、最低价的空值
    df['Open'].fillna(value=df['Close'], inplace=True)
    df['High'].fillna(value=df['Close'], inplace=True)
    df['Low'].fillna(value=df['Close'], inplace=True)
    #     df['marketCap'].fillna(value=df['marketCap'], inplace=True)

    # ===将停盘时间的某些列，数据填补为0
    fill_0_list = ['Volume'] + extra_fill_0_list
    df.loc[:, fill_0_list] = df[fill_0_list].fillna(value=0)
    # ===用前一天的数据，补全其余空值
    df.fillna(method='ffill', inplace=True)
    # ===去除上市之前的数据
    df = df[df['Ticker'].notnull()]
    # ===判断计算当天是否交易
    df['is_trade'] = 1
    df.loc[df['_merge'] == 'right_only', 'is_trade'] = 0
    del df['_merge']
    df.reset_index(drop=True, inplace=True)
    return df


# 将日线数据转换为其他周期的数据
def transfer_to_period_data(df, period_type='W', extra_agg_dict={}):
    # 将交易日期设置为index
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['trade_date'] = df['Date']
    df.set_index('trade_date', inplace=True)

    extra_agg_dict = extra_agg_dict
    period_type = period_type
    agg_dict = {
        'Date': 'last',
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'Value': 'sum',
        'Ticker': 'last',
        'is_trade': 'last',
        'pct_chg': 'last',
        # 'tom_istrade': 'last',
        # 'tom_open_chg': 'last',
    }
    agg_dict = dict(agg_dict, **extra_agg_dict)
    period_df = df.resample(rule=period_type).agg(agg_dict)

    # 计算必须额外数据
    period_df['trade_days'] = df['is_trade'].resample(period_type).sum()
    period_df['market_trade_days'] = df['Ticker'].resample(period_type).size()
    period_df = period_df[
        (period_df['market_trade_days'] > 0) & (period_df['trade_days'] > 0)]  # 有的时候整个周期不交易（例如春节、国庆假期），需要将这一周期删除

    # 计算周期资金曲线，回测的数据
    # period_df['everday_chg'] = df['pct_chg'].resample(period_type).apply(lambda x: list(x))
    # period_df['pct_chg'] = round(df['pct_chg'].resample(period_type).apply(lambda x: (x + 1).prod() - 1), 4)

    # ic分析需要的数据
    # period_df['pct_chg_5'] = 100 * df['pct_chg'].resample(period_type).apply(lambda x: (x + 1).prod() - 1).shift(-1)

    # 重新设定index
    period_df.reset_index(drop=True, inplace=True)
    period_df['Date'] = period_df['Date'].astype("str")
    #     period_df['交易日期'] = period_df['周期最后交易日']
    #     del period_df['周期最后交易日']

    return period_df


# 股价复权
def fuquan(df):
    df['pct_chg'] = df['Close'] / df['Close'].shift(1) - 1
    # 股票复权
    # df['fuquan'] = (1 + df['pct_chg']).cumprod()
    # df['Close'] = df['fuquan'] * (df.iloc[0]['Close'] / df.iloc[0]['fuquan'])
    # 其中 close是没复权的，Close是复权后的
    df['Open'] = df['Open'] / df['close'] * df['Close']
    df['High'] = df['High'] / df['close'] * df['Close']
    df['Low'] = df['Low'] / df['close'] * df['Close']

    return df


# 从文件夹获取股票数据，并处理
def get_ticker_data(allticker_path, start_date, end_date):
    all_data = pd.DataFrame()
    rename_dict = {
        'timestamp': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'adjusted_close': 'Close',
        'volume': 'Volume'
    }
    allticker_file = os.listdir(allticker_path)
    for code in allticker_file:
        # print(code)
        df = pd.read_csv(allticker_path + '/' + code, encoding='GBK', index_col=0)
        # df = pd.read_csv(allticker_path + '/ORGO.CSV', encoding='GBK', index_col=0)
        if len(df) > 50:
            df.rename(columns=rename_dict, inplace='True')
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            df['Ticker'] = code.split('.')[0]
            df.sort_values('Date', inplace=True)
            # 股票复权
            df = fuquan(df)
            # (2 * CLOSE + HIGH + LOW) / 4
            df['Value'] = ((2 * df['Close'] + df['High'] + df['Low']) / 4) * df['Volume']

            df = df[df['Volume'] > 0]
            df.reset_index(drop=True, inplace=True)
            # 计算指标

            df, extra_agg_dict = Postive_Functions(df, extra_agg_dict={})
            df, extra_agg_dict = get_pos_alpha(df, extra_agg_dict)

            # df = merge_with_index_data(df, index_data)
            # df['pct_chg'] = df['Close'] / df['Close'].shift(1) - 1

            df.dropna(inplace=True)
            # 将交易日期设置为index
            df = df[df['Date'] == end_date]
            df.reset_index(drop=True, inplace=True)

            # df = transfer_to_period_data(df, period_type='w', extra_agg_dict=extra_agg_dict)
            all_data = all_data.append(df)
        else:
            pass
    return all_data


# 去极值，处理离群值，将超出变量特定百分位范围的数值替换为其特定百分位数值。
def winsor(x):
    if x.dropna().shape[0] != 0:
        x.loc[x < np.percentile(x.dropna(), 5)] = np.percentile(x.dropna(), 5)
        x.loc[x > np.percentile(x.dropna(), 95)] = np.percentile(x.dropna(), 95)
    else:
        x = x.fillna(0)
    return x


# MAD去极值
# 截尾,nan用行业平均代替
def mad_cut(x):
    diff = (x - x.median()).apply(abs)
    mad = diff.median()
    upper_limit = x.median() + 1.4826 * mad
    lower_limit = x.median() - 1.4826 * mad
    x.loc[x < lower_limit] = lower_limit * 3.0
    x.loc[x > upper_limit] = upper_limit * 3.0
    x.clip(lower_limit, upper_limit, inplace=True)
    return x


# 标准化
def standardize(x):
    return (x - x.mean()) / x.std()


# 中性化
def norm(data):
    data = data.copy()
    """
    数据预处理，标准化
    """
    # 判断有无缺失值，若有缺失值，drop，若都缺失，返回原值

    datax = data.copy()
    if data.shape[0] != 0:
        ## 去极值
        data = data.apply(lambda x: winsor(x), axis=0)

        ## zscore
        data1 = (data - data.mean()) / data.std()

        # 缺失部分补进去
        data1 = data1.reindex(datax.index)
    else:
        data1 = data
    return data1


"""
调用norm中性化所有因子
"""


def NormFactors(datas):
    # datas = factorall.copy()
    fnormall = []

    dates = datas.Date.unique()
    for dateuse in dates:  # dateuse = dates[0]
        datause = datas.loc[datas.Date == dateuse]

        stockname = datause[['Date', 'Ticker']]
        fnorm = norm(datause.drop(['Date', 'Ticker'], axis=1))
        fnormall.append(pd.concat([stockname, fnorm], axis=1))
    fnormall = pd.concat(fnormall, axis=0)
    fnormall = fnormall.sort_values(by=['Date', 'Ticker'])
    return fnormall.reset_index(drop=True)


# 中性化
def OlsResid(y, x):
    df = pd.concat([y, x], axis=1)

    if df.dropna().shape[0] > 0:
        resid = sm.OLS(y, x, missing='drop').fit().resid
        return resid.reindex(df.index)
    else:
        return y


# 因子分布
def plot_factor(df, fname, ifcut=True):
    data = df.copy()
    data['year'] = data['Date'].apply(lambda x: x.split('-')[0])
    if ifcut:
        data[fname] = winsor(data[fname])

    year_l = data.year.unique()
    n_year = len(year_l)
    ncol = int(n_year / 3) + 1

    fig, axes = plt.subplots(3, ncol, figsize=(24, 10), sharex=False, sharey=False)

    for i in range(n_year):
        sns.kdeplot(data.loc[data.year == year_l[i], fname], shade=True, ax=axes[int(i / ncol), i % ncol],
                    label=year_l[i])
    plt.suptitle('Factor distribution:' + fname)


# 计算因子自相关性 #一阶自回归的时间序列
def get_factor_atuo_corr(factors):
    # factors = fnormall;ret = retdata
    """
    计算因子自相关性
    """
    factors = factors.copy()
    factors = factors.set_index(['Date', 'Ticker'])
    fac = []
    for i in factors.columns:
        s = factors.loc[:, i].unstack().T.corr()
        fac.append(pd.DataFrame(np.diag(s, 1), columns=[i], index=s.index[1:]))

    fac = pd.concat(fac, axis=1)
    return fac


# 计算IC
def getIC(factors, ret, method):
    # method = 'spearman';factors = fnorm;
    icall = pd.DataFrame()
    fall = pd.merge(factors, ret, left_on=['Date', 'Ticker'], right_on=['Date', 'Ticker'])
    icall = fall.groupby('Date').apply(lambda x: x.corr(method=method)['pct_chg_5']).reset_index()
    icall = icall.dropna().drop(['pct_chg_5'], axis=1).set_index('Date')
    return icall


# 画出因子自相关性图
def plot_atuo_corr(fac):
    # outputpath = output_picture
    """
    因子AC作图
    """
    for f in fac.columns:  # f = fac.columns[0]
        fig = plt.figure(figsize=(10, 5))
        fac[f].plot(legend=False, color='darkred')
        plt.title('因子auto_corr: ' + f)


# IC作图
def plotIC(ic_f):
    """
    IC作图
    """

    # fname = ic_f.columns[0]
    for fname in ic_f.columns:
        fig = plt.figure(figsize=(18, 8))
        ax = plt.axes()
        xtick = np.arange(0, ic_f.shape[0], 18)
        xticklabel = pd.Series(ic_f.index[xtick])
        plt.bar(np.arange(ic_f.shape[0]), ic_f[fname], color='red')
        ax.plot(np.arange(ic_f.shape[0]), ic_f[fname].rolling(4).mean(), color='green')
        ax1 = plt.twinx()
        ax1.plot(np.arange(ic_f.shape[0]), ic_f[fname].cumsum(), color='orange')
        ax.set_xticks(xtick)
        ax.set_xticklabels(xticklabel)
        plt.title(fname + '  IC = {},ICIR = {}'.format(round(ic_f[fname].mean(), 4),
                                                       round(ic_f[fname].mean() / ic_f[fname].std() * np.sqrt(52), 4)))


# IC分层
def getGroupIC(fdata, rt, method, groups):
    # groups = 5
    """
    因子分组IC，groups为分组数
    """
    rt = pd.concat([fdata, rt], axis=1).dropna()
    indexs = ["startdate"] + list(range(groups))
    if rt.shape[0] != 0:
        groupdata = pd.qcut(rt.iloc[:, 0], q=groups, labels=False, duplicates='drop')

        if groupdata.unique().shape[0] == groups:
            rt['group'] = groupdata
            IC = rt.groupby('group').apply(lambda x: x.corr(method=method).fillna(0).iloc[0, 1])

            result = pd.DataFrame([rt.columns[1]] + IC.tolist(), index=indexs).T

        else:
            result = pd.DataFrame([rt.columns[1]] + [0] * groups, index=indexs).T
    else:
        result = pd.DataFrame([rt.columns[1]] + [0] * groups, index=indexs).T

    return result.set_index('startdate')


# IC分层
def getGroupICSeries(factors, ret, method, groups):
    # method = 'spearman';factors = fnorm.copy();ret = ret
    icall = pd.DataFrame()

    dates = factors.Date.unique()
    ret = ret.pivot(index='Date', columns='Ticker', values='pct_chg_5')
    for dateuse in dates:  # dateuse = dates[0]

        fic = pd.DataFrame()
        fdata = factors.loc[factors.Date == dateuse, factors.columns[1:]].set_index('Ticker')

        rt = ret.loc[dateuse]
        for f in fdata.columns:  # f = fdata.columns[0]
            IC = getGroupIC(fdata[f], rt, method, groups)
            IC.insert(0, 'factor', f)
            fic = pd.concat([fic, IC], axis=0)

        icall = pd.concat([icall, fic], axis=0)

    return icall


# 分组IC作图
def plotGroupIC(groupIC):
    """
    分组IC作图
    """
    for f in groupIC.factor.unique():
        fig = plt.figure(figsize=(10, 5))
        groupIC.loc[groupIC.factor == f, groupIC.columns[1:]].mean(axis=0).plot(kind='bar')

        plt.title('Meverage of factor grouping IC: ' + f, fontsize=15)


# 一次性测试多个因子
def GroupTestAllFactors(factors, ret, groups):
    # factors = fnorm.copy();groups = 10
    """
    一次性测试多个因子
    """
    fnames = factors.columns
    fall = pd.merge(factors, ret, left_on=['Date', 'Ticker'], right_on=['Date', 'Ticker'])
    Groupret = []
    Groupturnover = []
    for f in fnames:  # f= fnames[2]
        if ((f != 'Ticker') & (f != 'Date')):
            fuse = fall[['Ticker', 'Date', 'pct_chg_5', f]]
            #            fuse['groups'] = pd.qcut(fuse[f],q = groups,labels = False)
            # 分组
            fuse['groups'] = fuse[f].groupby(fuse.Date).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            # 分组下期收益平均值
            result = fuse.groupby(['Date', 'groups']).apply(lambda x: x.pct_chg_5.mean())
            result = result.unstack().reset_index()
            if result.iloc[:, -1].mean() > result.iloc[:, -groups].mean():
                result['L-S'] = result.iloc[:, -1] - result.iloc[:, -groups]
                stock_l = fuse.loc[fuse.groups == 1]
            else:
                result['L-S'] = result.iloc[:, -groups] - result.iloc[:, -1]
                stock_l = fuse.loc[fuse.groups == groups]
            result.insert(0, 'factor', f)
            Groupret.append(result)

    Groupret = pd.concat(Groupret, axis=0).reset_index(drop=True)
    Groupret.dropna(inplace=True)

    Groupnav = Groupret.iloc[:, 2:].groupby(Groupret.factor).apply(lambda x: (1 + x / 100).cumprod())

    Groupnav = pd.concat([Groupret[['Date', 'factor']], Groupnav], axis=1)
    Groupnav.dropna(inplace=True)

    return Groupnav


# GroupTest作图
def plotnav(Groupnav):
    """
    GroupTest作图
    """
    for f in Groupnav.factor.unique():  # f = Groupnav.factor.unique()[0]
        fnav = Groupnav.loc[Groupnav.factor == f, :].set_index('Date').iloc[:, 1:]
        groups = fnav.shape[1] - 1
        lwd = [2] * groups + [4]
        ls = ['-'] * groups + ['--']

        plt.figure(figsize=(10, 5))
        for i in range(groups + 1):
            plt.plot(fnav.iloc[:, i], linewidth=lwd[i], linestyle=ls[i])
        plt.legend(list(range(groups)) + ['L-S'])
        plt.title('Factor layered testing / multi - space combination： ' + f, fontsize=15)


# 评价指标
def strategy_evaluate(df):
    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()

    ret_df = df[1].copy()
    ret_df['Date'] = pd.to_datetime(ret_df['Date'], format='%Y-%m-%d')

    for i in range(0, 6):
        results.loc[i, 'factor'] = df[0] + '_' + str(ret_df.columns[i + 2])
        # ===计算累积净值
        results.loc[i, 'cum_returns_final'] = round(ret_df[ret_df.columns[i + 2]].iloc[-1], 3)

        # ===计算年化收益
        annual_return = (ret_df[ret_df.columns[i + 2]].iloc[-1]) ** (
                '1 days 00:00:00' / (ret_df['Date'].iloc[-1] - ret_df['Date'].iloc[0]) * 365) - 1
        results.loc[i, 'Annual_return'] = str(round(annual_return * 100, 2)) + '%'

        # 计算当日之前的资金曲线的最高点
        ret_df['max2here'] = ret_df[ret_df.columns[i + 2]].expanding().max()
        # 计算到历史最高值到当日的跌幅，drowdwon
        ret_df['dd2here'] = ret_df[ret_df.columns[i + 2]] / ret_df['max2here'] - 1
        # 计算最大回撤，以及最大回撤结束时间
        end_date, max_draw_down = tuple(ret_df.sort_values(by=['dd2here']).iloc[0][['Date', 'dd2here']])

        results.loc[i, 'Max_drawdown'] = format(max_draw_down, '.2%')
        ret_df['pct_chg_{}'.format(i + 1)] = 100 * (
                ret_df[ret_df.columns[i + 2]] / ret_df[ret_df.columns[i + 2]].shift(1) - 1)

        ret_df.fillna(0, inplace=True)
        sharpe = round((ret_df['pct_chg_{}'.format(i + 1)] - 0.04 / 52).mean() / ret_df[
            'pct_chg_{}'.format(i + 1)].std() * np.sqrt(52), 3)

        results.loc[i, 'sharpe_ratio'] = sharpe

    return results


# 计算IC
def getfactor_return(factors, ret):
    df = pd.merge(factors, ret, left_on=['Date', 'Ticker'], right_on=['Date', 'Ticker'])
    return_df = pd.DataFrame()
    avg_mean = pd.DataFrame()
    fac_list = list(df.columns[2:-1])
    retu = 'pct_chg_5'
    for fac in fac_list:
        for i, df1 in enumerate(df.groupby('Date')):
            X = df1[1][fac].values
            X = standardize(X)
            Y = df1[1][retu].values
            result = sm.OLS(Y.astype(float), X.astype(float)).fit()  # 股票收益率和因子数据回归
            result = result.params[0]
            return_df.loc[i, 'Date'] = df1[0]
            return_df.loc[i, 'factor_return'] = result
        # 因子的平均收益
        avg_mean.loc[0, fac] = return_df['factor_return'].mean()

    return avg_mean


# if __name__ == '__main__':
#     allticker_path = r'D:\量化\my_team\code\data\day'
#     data_path = r'D:\量化\my_team\code\data'
#     index_path = r'D:\量化\my_team\code\data\index_data\NASDAQ.csv'
#     allticker_file = os.listdir(allticker_path)
#
#     start_date = '2019-05-25'
#     end_date = '2021-03-01'
#
#     index_data = get_index_data(index_path, start_date, end_date)
#     all_data = get_ticker_data(allticker_path, index_data, start_date, end_date)
#     factors_list = all_data.columns[12:]
#     factors_list = list(factors_list)
#     fac_list = ['Date', 'Ticker']
#     df = all_data.copy()
#     for fac in factors_list:
#         fac_list.append(fac)
#     df = NormFactors(df[fac_list])
#     big_list = ['TRIX', 'alpha005', 'AD', 'MINUS_DI', 'alpha020', 'alpha025', 'alpha033', 'alpha039', 'alpha088']
#     small_list = ['CCI', 'alpha001']
#
#     for factor in big_list:
#         df[factor + '_rank'] = df.groupby('Date')[factor].rank(pct=True)
#     for factor in small_list:
#         df[factor + '_rank'] = df.groupby('Date')[factor].rank(pct=True, ascending=False)
#     df['my_factor'] = df['CCI_rank'] + df['TRIX_rank'] + df['MINUS_DI_rank'] + df['AD_rank'] + df['alpha001_rank'] + df[
#         'alpha005_rank'] + df['alpha020_rank'] + df['alpha025_rank'] + df['alpha033_rank'] + df['alpha039_rank'] + df[
#                           'alpha088_rank']
#     df = df[['Date', 'Ticker', 'my_factor']]
#
#     df['rank'] = df.groupby('Date')['my_factor'].rank(ascending=False)
#     df = df[(df['rank'] <= 10)]  # 选取排名靠前的股票
#
#     # 挑选出选中股票
#     df['Ticker'] += ' '
#     group = df.groupby('Date')
#     select_stock = pd.DataFrame()
#     select_stock['buy_Ticker'] = group['Ticker'].sum()
#     select_stock['Ticker_number'] = group['Ticker'].size()
#     print(select_stock)

