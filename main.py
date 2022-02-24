from gmail import Gmail, GmailFilter
import os.path
from datetime import datetime

overWrite = True

def main():
    gmail = Gmail(credentials_file=os.path.dirname(__file__)+'/credentials.json', token_file=os.path.dirname(__file__)+'/token.json')
    filter = GmailFilter()
    originDate = datetime.strptime('01/01/2015', '%d/%m/%Y')
    filter.fromEmail('leboncoin').subject("Maison").fromDate(originDate)
    
    messages = gmail.listMessages(filter)
    
    filter = GmailFilter()
    filter.fromEmail('leboncoin').subject("Ventes immobilières").fromDate(originDate)
    messages.extend(gmail.listMessages(filter))

    print("retrieve %d messages " % len(messages))
    for msg in messages:
        print("msg %s" % msg['id'])
        try:
            gmail.saveMessageToFolder(folder='./results', msgId = msg['id'], overwrite=overWrite, savePayload = True)
        except FileExistsError as e:
            print("file error")
            print(e)
            print('continue...')
            continue
        except Exception as ee:
            print("error")
            print(ee)

if __name__ == '__main__':
    main()