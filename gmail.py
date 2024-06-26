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
        self.filters.append("after:%s" % datetime.strftime(date, '%Y-%m-%d'))
        
        return self
    
    def toDate(self, date: datetime):
        self.filters.append("before:%s" % datetime.strftime(date, '%Y-%m-%d'))
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
                print('creds need to update, refresh..')
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            print("Save the credentials for the next run")
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            print("Call the Gmail API")
            self.service = build('gmail', 'v1', credentials=creds)
            print('Gmail Service is ready')

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    def __del__(self):
        self.service.close()

    def getMessage(self, msgId):
        req = self.service.users().messages().get(userId='me', id=msgId)
        return req.execute()

    def _check_if_message_present_as_payload_file(self, msg, folder):
        file_dump =  self.getPayloadPath(msg=msg, folder=folder)
        return os.path.exists(file_dump)

    
    def _check_if_message_present_as_dump(self, msgId, folder):
        file_dump =  self.getDumpPath(msgId, folder)
        return os.path.exists(file_dump)


    def getDumpPath(self, msg, folder):
        return "%s/%s.%s" % (folder, msg['id'], 'json')

    def getPayloadPath(self, folder, msg):
        extension = GmailMessageExtractor.guess_mimetype_payload(msg)
        return "%s/%s.%s" % (folder, msg['id'], extension)

    def saveMessagePartsByMimeTypeToFolder(self, msg, mimetype, folder, overwrite=False):
        if not overwrite and self._check_if_message_present_as_payload_file(msg, folder):
            raise FileExistsError("mesgId %s Payload file already exists in : %s " % (msg['id'], folder))
        payload_path = self.getPayloadPath(folder, msg)
        parts = GmailMessageExtractor.get_parts_from_mimetype(msg, mimetype)
        dateMsgUnix = GmailMessageExtractor.extract_sent_timestamp(msg)
        for index, part in enumerate(parts):
            extension = GmailMessageExtractor.get_extension_for_mimetype(part['mimeType'])
            
            part_path = "%s/%s_part_%s.%s" % (folder, msg['id'], index, extension)
            if 'body' in part and 'data' in part['body']:
                data = part['body']['data']
                with open(part_path, 'w') as fp:
                    fp.write(GmailMessageExtractor.convert_frombase64_mail_item(data))
                os.utime(path=part_path, times = (dateMsgUnix, dateMsgUnix))

    def saveMessagePayloadToFolder(self, msg, folder, overwrite=False):
        if not overwrite and self._check_if_message_present_as_payload_file(msg, folder):
            raise FileExistsError("mesgId %s Payload file already exists in : %s " % (msg['id'], folder))
        payload_path = self.getPayloadPath(folder, msg)
        GmailMessageExtractor.extract_and_save_payload(msg, payload_path)
        dateMsgUnix = GmailMessageExtractor.extract_sent_timestamp(msg)
        os.utime(path=payload_path, times = (dateMsgUnix, dateMsgUnix))

    def saveMessageToFolder(self, msg, folder, overwrite=False):
        if not overwrite and self._check_if_message_present_as_dump(msg, folder):
            raise FileExistsError("mesgId %s Message file already exists in : %s " % (msg['id'], folder))
        subject = GmailMessageExtractor.extract_subject(msg)
        if subject is not None:
            print(subject)
        
        filedump_path = self.getDumpPath(msg, folder)
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
    def convert_frombase64_mail_item(data):
        decodedbytes = base64.urlsafe_b64decode(data)
        return str(decodedbytes, "utf-8")            

    @staticmethod
    def extract_payload(msg):
        payload = msg['payload']
        if 'data' not in payload['body']:
            raise Exception('no data in body')
        data = payload['body']['data']          
        return GmailMessageExtractor.convert_frombase64_mail_item(data)
        
    @staticmethod
    def get_parts_from_mimetype(msg, mimetype):
        parts = []
        payload = msg['payload']

        if 'parts' not in payload:
            raise Exception('no parts in body')
        for superpart in payload['parts']:
            if 'parts' in  superpart:
                parts.extend([part for part in superpart['parts'] if part['mimeType'] == mimetype])
                     
        return parts


    @staticmethod
    def get_extension_for_mimetype(mimetype):
        return 'html' if  mimetype == 'text/html' else 'txt'

    @staticmethod
    def guess_mimetype_payload(msg):
        payload = msg['payload']
        mimeType = payload['mimeType']
        return GmailMessageExtractor.get_extension_for_mimetype(mimeType)

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
