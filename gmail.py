from glob import escape
import os
import os.path
import string
from urllib.error import ContentTooShortError
from click import FileError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime
import base64
import json
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailFilter():
    
    def __init__(self):
        self.filters =[]
    def fromEmail(self, email):
        self.filters.append("from:%s" % email)
        return self
    
    def fromDate(self, date: datetime):
        self.filters.append("after:%d" % date.timestamp())
        return self
    
    def toDate(self, date: datetime):
        self.filters.append("before:%d" % date.timestamp())
        return self
    
    def isRead(self, read: bool = False):
        if not read:
            self.filters.append('is:unread')
        else:
            self.filters.append('is:read')
        return self

    def subject(self, subject):
        self.filters.append("subject:%s" % subject)
        return self

    def __str__(self) -> str:
        return ' '.join(self.filters)

class Gmail():

    def __init__(self, credentials_file: string , token_file: string):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            self.service = build('gmail', 'v1', credentials=creds)

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    def __del__(self):
        self.service.close()

    def getMessage(self, msgId):
        req = self.service.users().messages().get(userId='me', id=msgId)
        return req.execute()

    def _check_if_id_message_present_as_payload_file(self, msgId, folder):
        for x in os.listdir(folder):
            if msgId in x:
                return True
        return False
    
    def _check_if_id_message_present_as_dump(self, msgId, folder):
        return os.path.exists("%s/%s.json" % (folder, msgId))


    def getDumpPath(self, msgId, folder):
        return "%s/%s.%s" % (folder, msgId, 'json')

    def getPayloadPath(self, folder, msgId):
        msg = self.getMessage(msgId)
        extension = GmailMessageExtractor.guess_mimetype_payload(msg)
        return "%s/%s.%s" % (folder, msgId, extension)

    def saveMessagePayloadToFolder(self, msgId, folder, overwrite=False):
        if not overwrite and self._check_if_id_message_present_as_payload_file(msgId, folder):
            raise FileExistsError("mesgId %s Payload file already exists in : %s " % (msgId, folder))
        msg = self.getMessage(msgId)
        payload_path = self.getPayloadPath(folder, msgId)
        GmailMessageExtractor.extract_and_save_payload(msg, payload_path)
        dateMsgUnix = GmailMessageExtractor.extract_sent_timestamp(msg)
        os.utime(path=payload_path, times = (dateMsgUnix, dateMsgUnix))

    def saveMessageToFolder(self, msgId, folder, overwrite=False):
        if not overwrite and self._check_if_id_message_present_as_dump(msgId, folder):
            raise FileExistsError("mesgId %s Message file already exists in : %s " % (msgId, folder))
        msg = self.getMessage(msgId)
        
        subject = GmailMessageExtractor.extract_subject(msg)
        if subject is not None:
            print(subject)
        
        filedump_path = self.getDumpPath(msgId, folder)
        with open(filedump_path, 'w') as fp:
            json.dump(msg, fp)
        dateMsgUnix = GmailMessageExtractor.extract_sent_timestamp(msg)
        os.utime(path=filedump_path, times = (dateMsgUnix, dateMsgUnix))
        
        
    def listMessages(self, filter: GmailFilter = None):
        filterArg = None
        nbMsgRetrieved = 0
        allMessagesRetrieved = False
        messages=[]
        pageToken = None
        if filter is not None:
            filterArg = str(filter)

        while not allMessagesRetrieved:
            request = self.service.users().messages().list(userId='me', pageToken = pageToken, q=filterArg, maxResults = 400)
            response = request.execute()
            if 'messages' not in response:
                break
            messages.extend(response['messages'])
            nbMsgRetrieved = len(messages)
            if response['resultSizeEstimate'] <= nbMsgRetrieved:
                
                allMessagesRetrieved = True
                print('all retrieved')
            else:
                pageToken = response['nextPageToken'] 
                print('not all retrieved call next page %s' % pageToken)
            #pageToken

        return messages
        

class GmailMessageExtractor:
    
    @staticmethod
    def extract_sent_timestamp(msg):
        return float(msg['internalDate'])/1000

    @staticmethod
    def extract_payload(msg):
        payload = msg['payload']
        if 'data' not in payload['body']:
            raise Exception('no data in body')
        data = payload['body']['data']          
        decodedbytes = base64.urlsafe_b64decode(data)
        return str(decodedbytes, "utf-8")            

    @staticmethod
    def guess_mimetype_payload(msg):
        payload = msg['payload']
        mimeType = payload['mimeType']
        return 'html' if  mimeType == 'text/html' else 'txt'

    @staticmethod
    def extract_and_save_payload(msg, file):
        content = GmailMessageExtractor.extract_payload(msg)
        with open(file, 'w') as fp:
            fp.write(content)
            fp.close()

    @staticmethod
    def extract_subject(msg):
        payload = msg['payload']
        return payload['headers']['Subject'] if 'headers' in payload  and 'Subject' in payload['headers'] else None
