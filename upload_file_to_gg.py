
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
   
# For using listdir()
import os
   
  
# Below code does the authentication
# part of the code
gauth = GoogleAuth()
  
# Creates local webserver and auto
# handles authentication.
gauth.LoadCredentialsFile("client_secret.json")
#gauth.LocalWebserverAuth("client_secret.json")       
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
drive = GoogleDrive(gauth)
   
# replace the value of this variable
# with the absolute path of the directory
upload_file_list = ['get_finance_data.py']
for upload_file in upload_file_list:
	gfile = drive.CreateFile({'parents': [{'id': '1pzschX3uMbxU0lB5WZ6IlEEeAUE8MZ-t'}]})
	# Read file and set it as the content of this instance.
	gfile.SetContentFile(upload_file)
	gfile.Upload() # Upload the file.
