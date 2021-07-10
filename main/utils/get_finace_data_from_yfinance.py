
if data_type == 'day':
  for com in [NASDAQ_company,NYSE_company,AEMX_company]:
    for symbol in com.keys():
      print(symbol)
#         al = get_stock_price_info(symbol, period='max')
      end = None
      cl = get_data(stock_name=symbol, end=end, interval = '1d')
      cl.to_csv(day_data_path+'/'+symbol +'.CSV')
if data_type == 'tick':
  for com in [NASDAQ_company,NYSE_company,AEMX_company]:
    for symbol in com.keys():
      print(symbol)
      al = get_stock_price_info(symbol, period='5d',interval = '1m' )
      al.to_csv(tick_data_path+'/'+symbol +'.CSV')
if data_type == 'add_day':
  for com in [NASDAQ_company,NYSE_company,AEMX_company]:
    for symbol in com.keys():
      try:
         print(symbol)
         bl = pd.read_csv(day_data_path+symbol +'.CSV')
         import pdb;pdb.set_trace()
         date_time_str = bl['Date'][bl['Date'].index.max()].split(' ')[0]
         start = datetime.datetime.strptime(date_time_str,'%Y-%m-%d') + datetime.timedelta(days=1)
         start = str(start).split(' ')[0]
         end = None
         cl = get_data(stock_name=symbol, start=start, end=end, interval = '1d')
         cl = bl.append(cl)
         cl.to_csv(day_data_path+'/'+symbol +'.CSV')
      except Exception as r:
         print(r)

if data_type == 'add_tick':
  for symbol in NASDAQ_company.keys():
      try:
         print(symbol)
         bl = pd.read_csv(tick_data_path+symbol +'.CSV')
         date_time_str = bl['Datetime'][bl['Datetime'].index.max()].split(' ')[0]
         start = datetime.datetime.strptime(date_time_str,'%Y-%m-%d') + datetime.timedelta(days=1.5)
         end = None
         cl = get_data(stock_name=symbol, start=start, end=end)
         cl = bl.append(cl)
         cl.to_csv(tick_data_path+'/'+symbol +'.CSV')
      except Exception as r:
         print(r)
