import unittest
from lbc_message import LbcMessage 
from lxml import etree

class TestLbcMessage(unittest.TestCase):

    def test_init_old_ok(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        self.assertIsNotNone(lbc_msg.dom)

    def test_init_new_ok(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/new.html')
        self.assertIsNotNone(lbc_msg.dom)

    def test_find_search_items_old(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        self.assertIsNotNone(items)
        self.assertGreater(len(items), 0)

    def test_find_search_items_new(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/new.html')
        items = lbc_msg._find_search_items()
        self.assertIsNotNone(items)
        self.assertGreater(len(items), 0)

    def test_find_search_items_2(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        self.assertIsNotNone(items)
        for item in items:
            print('!!!')
            print(etree.tostring(item))


if __name__ == '__main__':
    unittest.main()

