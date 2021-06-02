
import pandas as pd
intraday = []
for i in ['FUBO']:#,'GAN','AAPL','TSLA','SKLZ','XPEV']:
   for z in range(1,3):
     for x in range(1,13):
        time = 'year'+str(z)+'month'+str(x)
        print(time)
        data = pd.read_csv('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol='+i+'&interval=1min&slice='+time+'&apikey=AD9PBTZE7CC87RXP')
        data.to_csv(i+'_'+time +'.CSV')
