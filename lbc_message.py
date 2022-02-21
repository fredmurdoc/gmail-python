from bs4 import BeautifulSoup
from lxml import etree

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
        return self.dom.xpath('//td/a[contains(@href, "[MYSRCH]")]/../..')
    