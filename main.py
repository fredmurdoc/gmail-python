from gmail import Gmail, GmailFilter

from datetime import datetime

overWrite = False

def main():
    gmail = Gmail()
    filter = GmailFilter()
    originDate = datetime.strptime('01/01/2015', '%d/%m/%Y')
    filter.fromEmail('no.reply@leboncoin.fr').fromDate(originDate)
    filter.fromEmail('leboncoin').subject("Maison").fromDate(originDate)
    #filter.fromEmail('leboncoin').fromDate(originDate)
    #filter.subject("Ventes immobilières ")
    messages = gmail.listMessages(filter)


    print("retrieve %d messages " % len(messages))
    for msg in messages:
        print("msg %s" % msg['id'])
        try:
            gmail.saveMessageToFolder(folder='./results', msgId = msg['id'], overwrite=overWrite)
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