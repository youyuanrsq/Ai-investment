from factors import *
from alpha101 import *
from usa_fun import *
import datetime
from datetime import timedelta

def get_stocks_list(end_date, allticker_path, stocks_num, acs=False):
    allticker_path = allticker_path
    # allticker_file = os.listdir(allticker_path)
    start_date = (pd.to_datetime(end_date, format="%Y-%m-%d") - timedelta(days=500)).strftime('%Y-%m-%d')
    end_date = end_date
    all_data = get_ticker_data(allticker_path, start_date, end_date)

    # 多因子列表
    factors_list = all_data.columns[12:]
    factors_list = list(factors_list)
    fac_list = ['Date', 'Ticker']
    df = all_data.copy()

    # 不进行去极值与标准化
    # for fac in factors_list:
    #     fac_list.append(fac)
    # # 因子标准化
    # df = NormFactors(df[fac_list])

    # 多因子的构建
    big_list = ['TRIX', 'alpha005', 'AD', 'MINUS_DI', 'alpha020', 'alpha025', 'alpha033', 'alpha039', 'alpha088']
    small_list = ['CCI', 'alpha001']

    for factor in big_list:
        df[factor + '_rank'] = df.groupby('Date')[factor].rank(pct=True)
    for factor in small_list:
        df[factor + '_rank'] = df.groupby('Date')[factor].rank(pct=True, ascending=False)
    df['my_factor0'] = df['CCI_rank'] + df['TRIX_rank'] + df['MINUS_DI_rank'] + df['AD_rank'] + df['alpha001_rank'] + df[
        'alpha005_rank'] + df['alpha020_rank'] + df['alpha025_rank'] + df['alpha033_rank'] + df['alpha039_rank'] + df[
                          'alpha088_rank']
    df['my_factor'] = df['alpha005_rank']
    df = df[['Date', 'Ticker', 'my_factor']]

    # 选出排名较高的股票
    df['rank'] = df.groupby('Date')['my_factor'].rank(ascending=acs)
    df = df[(df['rank'] <= stocks_num)]  # 选取排名靠前的股票

    # 挑选出选中股票
    df['Ticker'] += ' '
    group = df.groupby('Date')
    select_stock = pd.DataFrame()
    select_stock['buy_Ticker'] = group['Ticker'].sum()
    select_stock['Ticker_number'] = group['Ticker'].size()
    stocks_list = select_stock['buy_Ticker'].values.tolist()[0].split()
    return stocks_list


if __name__ == '__main__':
    # 股票文件夹的路径
    allticker_path = r'D:\量化\my_team\code\data\day'
    # 获取当日得分高的票
    end_date = '2021-06-04'
    # 选择n个股票
    n = 20
    # 是否反向选股做空，True表示选择得分低的做空，False表示选择得分高的做多
    asc = False
    stocks_list = get_stocks_list(end_date, allticker_path, stocks_num=n, acs=asc)
    print(stocks_list)
