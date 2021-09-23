import xml.sax as SX
from xml.sax.handler import ContentHandler

class CatalogHandler(ContentHandler):
    def __init__(self):        
        self.state = 0
        ContentHandler.__init__(self)

    def startElement(self, name, attrs): 
        if self.state == 0:
            if(name == "Items"):
                self.state = 1
        elif self.state == 1:
            if(name == "Item"):
                self.state = 2
                self.catalogProperties = dict()
        elif self.state == 2:
            self.currentProperty = name
            self.currentPropertyValue = ""
            self.state = 3

    def characters(self, content):
        if self.state == 3:
             self.currentPropertyValue = self.currentPropertyValue + content

    def endElement(self, name):        
        if self.state == 3:
            self.state = 2
            self.catalogProperties[self.currentProperty] = self.currentPropertyValue            
        elif self.state == 2:
            self.onCatalogItem(self.catalogProperties)
            self.state = 1
        elif self.state == 1:
            self.state = 0

    def onCatalogItem(self, item):
        print(item)

#req = urllib.request.urlopen('http://pricesprodpublic.blob.core.windows.net/pricefull/PriceFull7290027600007-413-202109230340.gz?sv=2014-02-14&sr=b&sig=vpdOhZqh50Aoz0gJcA6aLdUsG0vRZRYsNdBjQZ8816U%3D&se=2021-09-23T06%3A47%3A25Z&sp=r')
#requnzipped = gzip.GzipFile('data.gz', 'rb', 1, req)
#SX.parse(requnzipped, CatalogHandler())
