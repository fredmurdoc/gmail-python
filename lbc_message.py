from bs4 import BeautifulSoup
from lxml import etree
import re
class LbcMessageXpathFinder:
    ITEMS_PARENT_TAG_TR = '//td/a[contains(@href, "[MYSRCH]")]/../..'
    ITEM_IMAGE_STYLE = './td[1]/div'
    ITEM_DESCRIPTION = './td[2]/a/span[1]'
    ITEM_PRIX = './td[2]/a/span[2]'
    ITEM_COMMUNE = './td[2]/a/div/span[1]'
class LbcMessage:
    
    def loadFromFile(self, file):
        with open(file, 'r') as fp:
            content = fp.read()
            self.loadFromString(content)
            fp.close()    
    
    def loadFromString(self, payload):
        soup = BeautifulSoup(payload, "html.parser")
        self.dom = etree.HTML(str(soup))
    
    def _find_search_items(self):
        return self.dom.xpath(LbcMessageXpathFinder.ITEMS_PARENT_TAG_TR)

    def _find_search_item_description(self, parent_item):
        element = parent_item.find(LbcMessageXpathFinder.ITEM_DESCRIPTION)
        return element.text if element is not None else None

    def _find_search_item_prix(self, parent_item):
        element = parent_item.find(LbcMessageXpathFinder.ITEM_PRIX)
        return element.text if element is not None else None

    def _find_search_item_commune(self, parent_item):
        element = parent_item.find(LbcMessageXpathFinder.ITEM_COMMUNE)
        return element.text if element is not None else None

    def _find_search_item_image_url(self, parent_item):
        element =  parent_item.find(LbcMessageXpathFinder.ITEM_IMAGE_STYLE)
        style_string = element.attrib['style']
        for style_attr_raw in style_string.split(';'):
            style_attr = style_attr_raw.strip()
            if 'background-image:' in style_attr:
                value = style_attr[len('background-image:'):]
                if value is None:
                    return value
                reg_val =re.search('url\((.+)\)', value.strip())
                if reg_val is None:
                    return None
                return reg_val.group(1)    