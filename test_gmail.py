import unittest
from gmail import Gmail, GmailFilter 
from datetime import datetime
import os.path
class TestGmailFilter(unittest.TestCase):

    def test_fromdate(self):
        filter = GmailFilter()
        date = datetime.now()
        filter.fromDate(date)
        self.assertEqual("after:%d" % date.timestamp(), str(filter))

    def test_todate(self):
        filter = GmailFilter()
        date = datetime.now()
        filter.toDate(date)
        self.assertEqual("before:%d" % date.timestamp(), str(filter))

    def test_isreadtrue(self):
        filter = GmailFilter()
        filter.isRead(True)
        self.assertEqual('is:read' , str(filter))

    def test_isreadfalse(self):
        filter = GmailFilter()
        filter.isRead(False)
        self.assertEqual('is:unread' , str(filter))

    def test_fromemail(self):
        filter = GmailFilter()
        filter.fromEmail('bob@example.com')
        self.assertEqual('from:bob@example.com' , str(filter))

    def test_chained(self):
        filter = GmailFilter()
        date = datetime.now()
        filter.fromDate(date).isRead(True).fromEmail('bob@example.com')
        self.assertEqual("after:%d is:read from:bob@example.com" % date.timestamp() , str(filter))

class TestGmail(unittest.TestCase):

    def test_init(self):
        self.assertIsNotNone(Gmail())

    def test_filter(self):
        gmail = Gmail()
        filter = GmailFilter()
        filter.fromEmail('no.reply@leboncoin.fr')
        messages = gmail.listMessages(filter)
        self.assertIsNotNone(messages)
        self.assertGreater(len(messages), 0)
        self.assertIsNotNone(messages[0])
        print(messages[0])
    
    def test_getmessage(self):
        gmail = Gmail()
        filter = GmailFilter()
        filter.fromEmail('no.reply@leboncoin.fr')
        messages = gmail.listMessages(filter)
        msg = gmail.getMessage(messages[0]['id'])
        self.assertIsNotNone(msg)
        print(msg)

    def test_savemessagetotemp(self):
        gmail = Gmail()
        filter = GmailFilter()
        filter.fromEmail('no.reply@leboncoin.fr')
        messages = gmail.listMessages(filter)
        gmail.saveMessageToFolder(folder='/tmp', msgId = messages[0]['id'])
        self.assertTrue(os.path.exists("/tmp/%s.html" % messages[0]['id']))


if __name__ == '__main__':
    unittest.main()