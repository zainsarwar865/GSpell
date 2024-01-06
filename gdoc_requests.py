from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import json

# Insert your API Key here
# This is a sample API
API = "A9dj383jd9aUuvMNR3rL-0QrsmCBk3kdkwo9Q" 
SCOPES = [ 'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents']


# Add your title token and credentials path here
token_path = "token_title.json"
creds_path = "credentials.json"



def change_doc_title(doc_id, new_title):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    # Load auth token
    token_file = open(token_path)
    token_dict = json.load(token_file)
    auth_token = token_dict['token']

    complete_url = f"https://www.googleapis.com/drive/v3/files/{doc_id}?key={API}" 
    data =  {"name" : new_title} 
    headers = {"Authorization" : "Bearer " + auth_token,
            "Accept" : "application/json",
            "Content-Type" : "application/json"}
    myobj = json.dumps(data)
    r = requests.patch(url = complete_url, headers=headers, data=myobj)
    status = r.status_code
    return status







