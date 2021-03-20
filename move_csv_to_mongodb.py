from vnpy.trader.constant import (Exchange, Interval)
import pandas as pd
from vnpy.trader.database import database_manager
from vnpy.trader.object import (BarData, TickData)
from datetime import datetime, timedelta, timezone
import os


def from_local_read_company_name(filepath='D:\\pycharmprojects\\backtrader-general-api\\data\\stocks\\'):
    filenames = os.listdir(filepath)
    company_names = []
    for filename in filenames:
        company = filename.split('.')[0]
        company_names.append(company)
    return company_names


def move_df_to_sqlite(imported_data: pd.DataFrame):
    """
    Import the CSV file into mongodb database
    """
    bars = []
    start = None
    count = 0

    for row in imported_data.itertuples():
        # Add time zone
        utc_8 = timezone(timedelta(hours=8))
        bar = BarData(
            symbol=row.Symbol,
            exchange=row.Exchange,
            datetime=row.Date.replace(tzinfo=utc_8),
            interval=row.Interval,
            volume=row.Volume,
            open_price=row.Open,
            high_price=row.High,
            low_price=row.Low,
            close_price=row.Close,
            open_interest=row.Open_interest,
            gateway_name="DB",
        )
        bars.append(bar)

        # do some statistics
        count += 1
        if not start:
            start = bar.datetime
    end = bar.datetime

    # insert into database
    database_manager.save_bar_data(bars)

    print(f'Insert Bar: {count} from {start} - {end}')


def main(symbol, data_path):
    # Read the CSV file that needs to be stored in the database
    imported_data = pd.read_csv(data_path + f'{symbol}.csv')
    # Add a list of exchanges
    imported_data['Exchange'] = Exchange.SMART
    # Add a list of inteval
    imported_data['Interval'] = Interval.DAILY
    # Add a list of open_interest
    imported_data['Open_interest'] = 0.0
    # Add a list of symbol
    imported_data['Symbol'] = f'{symbol}-USD-STK'
    # A column of the float data type is explicitly required
    float_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Open_interest']
    for col in float_columns:
        imported_data[col] = imported_data[col].astype('float')
    # Specify the format of the timestamp
    # %Y -% m -% d% H: M: s means that the time stamp in your CSV data must be in 2020-05-01 08:32:30 format
    datetime_format = '%Y-%m-%d %H:%M:%S'
    imported_data['Date'] = pd.to_datetime(imported_data['Date'], format=datetime_format)

    # List the column name of each column
    imported_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits',
                             'Exchange', 'Interval', 'Open_interest', 'Symbol']

    move_df_to_sqlite(imported_data)


if __name__ == "__main__":
    data_path = 'D:\\pycharmprojects\\backtrader-general-api\\data\\ARKQ\\'
    symbols = from_local_read_company_name(data_path)
    for symbol in symbols:
        main(symbol, data_path)

