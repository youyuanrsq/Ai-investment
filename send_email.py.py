#!/usr/bin/env python
# coding: utf-8

# In[97]:


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import numpy as np
import glob
import pandas as pd
import datetime
import json
from datetime import date

class Email:
    
    def __init__(self):
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login('BeyondSea_Trading@outlook.com', 'JZBvaan0092')
        self.server = server
        self.email_sender = 'BeyondSea_Trading@outlook.com'
    
    def send_email(self, email_recipient,
                   email_subject,
                   email_message,
                   attachment_location = ''):

        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = email_recipient
        msg['Subject'] = email_subject

        msg.attach(MIMEText(email_message, 'plain'))

        if attachment_location != '':
            filename = os.path.basename(attachment_location)
            attachment = open(attachment_location, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            "attachment; filename= %s" % filename)
            msg.attach(part)

        try:

            text = msg.as_string()
            self.server.sendmail(self.email_sender, email_recipient, text)
            print('email sent')
            self.server.quit()
        except Exception as e:
            print(e)
            print("SMPT server connection error")
        return True

    
def change_time_to_number(time):
    # time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame({'time': [pd.to_datetime(time)]})
    df_unix_sec = pd.to_numeric(df['time']) [0]
    return df_unix_sec


def compose_email(trading_action):
    s = ','
    direction = trading_action['Direction']
    price = round(trading_action['Price'],3)
  
    subject = direction +' '+ trading_action['Symbol'] + ' at price: ' + str(price)
    if direction == 'buy':
        stop_loss_range = round(trading_action['stop_loss_range'] ,3)
        stop_earning_range = round(trading_action['stop_earning_range'] ,3)
        info = ('Price: ' + str(price) , ' \nTrading size: ' +  str(trading_action['Size']), ' \nCurrent postion: ' +  str(trading_action['Position']),
                ' \nStop_loss_price: ' + str(stop_loss_range),
                ' \nStop_earning_range: ' + str(stop_earning_range)
               )
    elif direction == 'sell':
        info = ('Price: ' + str(price) , ' \nTrading size: ' +  str(trading_action['Size']),
                ' \nCurrent postion: ' + str(trading_action['Position'])
               )
    content = s.join(info)
    return subject, content


def compose_summary_email(trading_info):
    s = ','
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    subject = d1 + ' Trading Summary'
    content = []
    for i in trading_info:
        info = ('\nSymbol: ' + i[0] , ' \nTrading earning ratio: ' +  str(i[1]), ' \nStock change ratio: ' +  str(i[2])
       )
        info = s.join(info)
        content.append(info)
    content = s.join(content)
    return subject, content
        
        


# In[68]:



# define users and what stocks should be provided
users = {'jiangzhubo1992@gmail.com':'all'}
#          '973099449@qq.com':'all', 
#          '1033904749@qq.com':'all', 
#          '1140623243@qq.com':'all', 
#          'qiuansong@qq.com':'all',
#            'junelai999@gmail.com':'all', 
#          'fengyuxian1992@gmail.com':'all', 
#          'orangekate77@gmail.com':'all', 
#          'shaohua@gmail.com':'all'}
      


# step 1 :send action points to users

# In[ ]:



##
recent_stock_update = {}
start_time = change_time_to_number(datetime.date.today().strftime("%Y-%m-%d 09:30:00"))
while True:
    for path in glob.glob('/home/zhubo/Documents/fda_check/test2/comparie/*.json'):
        try:
            stock_path = path
            stock = stock_path.split('/')[-1].split('.')[0]
            if stock not in list(recent_stock_update.keys()):
                recent_stock_update[stock] = start_time
            with open(stock_path) as f:       
                   data = json.load(f)
            time_key = [[change_time_to_number(time), time] for time in list(data.keys())]
            current_time = sorted(time_key , key = lambda x : x[0])[-1]
            if current_time[0] > recent_stock_update[stock]:
                recent_stock_update[stock] = current_time[0]
                trading_action = data[current_time[1]]
                subject, content = compose_email(trading_action)
                for user in users.keys():
                   
                    if users[user] == 'all':
                        e= Email()
                        e.send_email(user,
                                   subject,
                                   content, 
                                   '')
                    print('send email to', user)
        except Exception as e:
            print(e)


# In[101]:


def return_stock_summary(path):
        stock_path = path
        stock = stock_path.split('/')[-1].split('.')[0]
        with open(stock_path) as f:       
               data = json.load(f)
        time_key = [[change_time_to_number(time), time] for time in list(data.keys()) if time not in ['open','close']]
        trade_time = sorted(time_key , key = lambda x : x[0])
        if  data[trade_time[0][1]]['Direction'] == 'buy':
            open_postion = data[trade_time[0][1]]['Position'] -1
        elif  data[trade_time[0][1]]['Direction'] == 'sell':
            open_postion = data[trade_time[0][1]]['Position'] +1

        total_buy = open_postion * data['open'] 
        stock_change_ratio = (data['close'] - data['open']) * 100 / data['open']
        total_sell = 0 
        buy_size = open_postion
        sell_size = 0
        for i in trade_time:
            trade_index = i[1]
            if data[trade_index]['Direction'] == 'buy':
               total_buy += data[trade_index]['Price'] * data[trade_index]['Size']
               buy_size += data[trade_index]['Size']
            elif data[trade_index]['Direction'] == 'sell':
               total_sell += data[trade_index]['Price'] * data[trade_index]['Size']
               sell_size += data[trade_index]['Size']
        if buy_size >= sell_size:
            close_size = buy_size - sell_size
            close_sell = close_size * data['close']
            total_sell += close_sell     
            final_earning = total_sell - total_buy
            print(close_size , data['open'])
            if close_size > 0:
               basic_earning_ratio = final_earning * 100 / (close_size * data['open'])
            else:
               basic_earning_ratio = final_earning * 100 / (open_postion * data['open']) 

            print(data[trade_index]['Symbol']+' earning', final_earning, basic_earning_ratio, stock_change_ratio)
            return data[trade_index]['Symbol'], round(basic_earning_ratio ,2), round(stock_change_ratio,2)
        if buy_size < sell_size:
            print('something wrong with position')
            return data[trade_index]['Symbol'], 0, round(stock_change_ratio,2)
def send_summary(log_path):
    trading_info = []
    for path in glob.glob(log_path + '*.json'):
        trading_info.append(return_stock_summary(path))
    subject, content = compose_summary_email(trading_info)
    for user in users.keys():
        print(subject, content)
        if users[user] == 'all':
            e= Email()
            e.send_email(user,
                       subject,
                       content, 
                       '')
        print('send email to', user)


# Step 2: send summary email to user

# In[103]:


send_summary('/home/zhubo/Documents/fda_check/test2/comparie/')
