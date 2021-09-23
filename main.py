# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from flask import request

from google.cloud import ndb
import json
import logging
import xml.etree.ElementTree as ET
import xml.sax as SX
import xmlimporter
import io
import json
import urllib.request
import gzip

client = ndb.Client()
app = Flask(__name__)

def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware

app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)  # Wrap the app in middleware.


class CatalogProduct(ndb.Model):
    barcode = ndb.StringProperty()
    productName = ndb.StringProperty()
    brandName = ndb.StringProperty()
    qty = ndb.StringProperty()
    qtyUnit = ndb.StringProperty()

class XmlApiImporter(xmlimporter.CatalogHandler):
    def __init__(self):
        xmlimporter.CatalogHandler.__init__(self)
        self.bulk = []

    def onCatalogItem(self, itemAttributes):
        item = CatalogProduct()
        item.barcode = itemAttributes["ItemCode"]
        item.productName = itemAttributes["ItemName"]
        item.brandName = itemAttributes["ManufacturerName"]
        item.qty = itemAttributes["Quantity"]
        item.qtyUnit = itemAttributes["UnitOfMeasure"]
        item.key = ndb.Key('CatalogProduct', item.barcode)            
        self.bulk.append(item)

        if len(self.bulk)>64:
            self.flush()

    def flush(self):
        if len(self.bulk) > 0:
            ndb.put_multi(self.bulk)                
            self.bulk = []

def import_catalog_file(fileobj):
    xmlApiImporter = XmlApiImporter()
    SX.parse(fileobj, xmlApiImporter)
    xmlApiImporter.flush()

@app.route('/api/v1/qitem/<item>')
def api_item_query(item):
    prod = CatalogProduct.get_by_id(item)
    return prod.to_dict()

@app.route('/admin/import_url', methods=["POST"])
def import_url():
    postjson = request.get_json()
    url = postjson["url"]
    req = urllib.request.urlopen(url)
    unzipped = gzip.GzipFile('data.gz', 'rb', 9, req)
    import_catalog_file(unzipped)
    return { "status":  "ok" }


