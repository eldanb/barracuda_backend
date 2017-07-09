/**
 * Copyright 2017, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

const express = require('express');
const Datastore = require('@google-cloud/datastore');

const app = express();
const datastore = Datastore();

app.get('/', (req, res) => {
  res.status(200).send('Hello, world 3!!!').end();
});

app.post('/admin/import', (req, res) => {
    var body="";
    
    req.on('data', function (data) {        
        body += data;
        // 1e6 === 1 * Math.pow(10, 6) === 1 * 1000000 ~~~ 1MB
        if (body.length > 1e7) { 
            // FLOOD ATTACK OR FAULTY CLIENT, NUKE REQUEST
            req.connection.destroy();
        }
    });
    
    req.on('end', function () {
        var lines = body.split("\n");
        var headers = lines.shift().split("\t");
        var bulk = [];
        
        while(lines.length) {
            var line = lines.shift().split("\t");
            var lineobj = {};
            for(var i=0; i<headers.length; i++) {
                lineobj[headers[i]] = line[i];
            }

            bulk.push(lineobj);
            if(!lines.length || bulk.length>256) {
                var savedObjects = bulk.map(function(l) {
                    return {
                        key: datastore.key(["CatalogProduct", l.barcode]),
                        data: l
                    };
                });

                datastore.insert(savedObjects);
                
                bulk = [];
            }
        }

        res.status(200).send('Done!!!').end();
        
    });  
});

// Start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}`);
  console.log('Press Ctrl+C to quit.');
});
// [END app]
