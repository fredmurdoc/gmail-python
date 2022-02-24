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

    def test_find_search_item_image_url_old(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        print('##############')
        print(items[0].tag)
        print(etree.tostring(items[0]))
        value = lbc_msg._find_search_item_image_url(items[0])
        self.assertIsNotNone(value)
        self.assertEquals('https://img.leboncoin.fr/api/v1/lbcpb1/images/93/6c/48/936c485fec35759f7901d90e5e0276c0fef37ec5.jpg?rule=ad-small', value)

    def test_find_search_item_description_old(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        print('##############')
        print(items[0].tag)
        print(etree.tostring(items[0]))
        value = lbc_msg._find_search_item_description(items[0])
        self.assertIsNotNone(value)
        self.assertEquals('Maison 1 pièce 60 m²', value)

    def test_find_search_item_description_old(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        print('##############')
        print(items[0].tag)
        print(etree.tostring(items[0]))
        value = lbc_msg._find_search_item_description(items[0])
        self.assertIsNotNone(value)
        self.assertEquals('Maison 1 pièce 60 m²', value)

    def test_find_search_item_prix(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        print('##############')
        print(items[0].tag)
        print(etree.tostring(items[0]))
        value = lbc_msg._find_search_item_prix(items[0])
        self.assertIsNotNone(value)
        self.assertEquals('58000 €', value)

    def test_find_search_item_commune(self):
        lbc_msg = LbcMessage()
        lbc_msg.loadFromFile('tests/old.html')
        items = lbc_msg._find_search_items()
        print('##############')
        print(items[0].tag)
        print(etree.tostring(items[0]))
        value = lbc_msg._find_search_item_commune(items[0])
        self.assertIsNotNone(value)
        self.assertEquals('Treffieux 44170', value)


if __name__ == '__main__':
    unittest.main()

