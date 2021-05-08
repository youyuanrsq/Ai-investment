#!/usr/bin/env python
# coding: utf-8

# In[47]:


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path



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


# In[ ]:


'junelai999@gmail.com':'all', 
      'fengyuxian1992@gmail.com':'all', 
      'orangekate77@gmail.com':'all', 
      'shaohua@gmail.com':'all'}


# In[36]:



# define users and what stocks should be provided
users = {'409980834@qq.com':'all', 
         '973099449@qq.com':'all', 
         '1033904749@qq.com':'all', 
         '1140623243@qq.com':'all', 
         'qiuansong@qq.com':'all'}
      


# In[35]:


test_users = {'409980834@qq.com':'all'}


# In[37]:


def compose_email(symbol = 'fubo',
                    price = '29',
                    stop_loss_range = '26-28',
                    stop_earning_range = '30-31',
                    direction = 'buy',
                    size = '1',
                    position = '1',
                    risk = '60%'
                ):
    s = ','
    subject = symbol +' '+ direction
    info = ('Price: ' + price , ' Trading size: ' +  size, ' Current postion: ' + position)
    content = s.join(info)
    return subject, content


# In[51]:



for user in users.keys():
    print('send email to', user)
    if users[user] == 'all':
        subject, content =  compose_email()
        e= Email()
        e.send_email(user,
                   subject,
                   content, 
                   '')
