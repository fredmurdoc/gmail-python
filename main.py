from gmail import Gmail, GmailFilter

def main():
    gmail = Gmail()
    filter = GmailFilter()
    filter.fromEmail('no.reply@leboncoin.fr')
    messages = gmail.listMessages(filter)
    for msg in messages:
        gmail.saveMessageToFolder(folder='./results', msgId = msg['id'])

if __name__ == '__main__':
    main()