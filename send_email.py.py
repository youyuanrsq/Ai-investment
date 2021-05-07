#!/usr/bin/env python
# coding: utf-8

# In[18]:


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path


def send_email(email_recipient,
               email_subject,
               email_message,
               attachment_location = ''):

    email_sender = 'BeyondSea_Trading@outlook.com'

    msg = MIMEMultipart()
    msg['From'] = email_sender
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
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login('BeyondSea_Trading@outlook.com', 'JZBvaan0092')
        text = msg.as_string()
        server.sendmail(email_sender, email_recipient, text)
        print('email sent')
        server.quit()
    except Exception as e:
        print(e)
        print("SMPT server connection error")
    return True


# In[33]:


users = ['409980834@qq.com', '973099449@qq.com', '1033904749@qq.com','1140623243@qq.com', 'qiuansong@qq.com','junelai999@gmail.com',
'fengyuxian1992@gmail.com', 'orangekate77@gmail.com', 'shaohua@gmail.com']


# In[35]:


test_users = ['409980834@qq.com']


# In[30]:


symble = 'fubo'
price = str(29)
stop_loss_range = '26-28'
stop_earning_range = '30-31'
direction = 'buy'
size = '1'
position = '1'
risk = '60%'
s = ','
subject = symble +' '+ direction
info = ('Price: ' + price , ' Trading size: ' +  size, ' Current postion: ' + position)
content = s.join(info)


# In[40]:


for user in test_users:
    send_email(user,
               subject,
               content, 
               '')

