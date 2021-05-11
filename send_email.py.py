#!/usr/bin/env python
# coding: utf-8

# In[117]:


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import numpy as np
import glob
import pandas as pd

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
    df = pd.DataFrame({'time': [pd.to_datetime(time)]})
    df_unix_sec = pd.to_datetime(df['time']).astype(int)/ 10**9
    return list(df_unix_sec)[0]


def compose_email ( stock,
                    price = '29',
                    stop_loss_range = '26-28',
                    stop_earning_range = '30-31',
                    direction = 'buy',
                    size = '1',
                    position = '1',
                    risk = '60%'
                ):
    s = ','
    subject = direction +' '+ stock + ' at price: ' + str(price)
    info = ('Price: ' + str(price) , ' \nTrading size: ' +  str(size), ' \nCurrent postion: ' + str(position),
            ' \nStop_loss_price: ' + str(stop_loss_range),
            ' \nStop_earning_range: ' + str(stop_earning_range),
           
           )
    content = s.join(info)
    return subject, content


# In[131]:



# define users and what stocks should be provided
users = {'409980834@qq.com':'all', 
         '973099449@qq.com':'all', 
         '1033904749@qq.com':'all', 
         '1140623243@qq.com':'all', 
         'qiuansong@qq.com':'all',
           'junelai999@gmail.com':'all', 
         'fengyuxian1992@gmail.com':'all', 
         'orangekate77@gmail.com':'all', 
         'shaohua@gmail.com':'all'}
      


# In[133]:



recent_stock_update = {}
while True:
    for path in glob.glob('/home/zhubo/Documents/fda_check/test2/comparie/*.json'):
        try:
            stock_path = path
            stock = stock_path.split('/')[-1].split('.')[0]
            if stock not in list(recent_stock_update.keys()):
                recent_stock_update[stock] = 0
            with open(stock_path) as f:       
                   data = json.load(f)

            time_key = [[change_time_to_number(time), time] for time in list(data.keys())]
            current_time = sorted(time_key , key = lambda x : x[0])[-1]
            if current_time[0] > recent_stock_update[stock]:
                recent_stock_update[stock] = current_time[0]
                trading_action = data[current_time[1]]
                print(trading_action)
                subject, content = compose_email( trading_action['Symbol'],
                                price = trading_action['Price'],
                                stop_loss_range = trading_action['stop_loss_range'],
                                stop_earning_range = trading_action['stop_earning_range'],
                                direction = trading_action['Direction'],
                                size = trading_action['Size'],
                                position = trading_action['Position'],
                                risk = '60%')
                print(subject,content)
                for user in users.keys():
                    print('send email to', user)
                    if users[user] == 'all':
                        #subject, content =  compose_email()
                        e= Email()
                        e.send_email(user,
                                   subject,
                                   content, 
                                   '')
        except Exception as e:
            print(e)
