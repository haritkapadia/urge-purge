const express = require('express');
const http = require('http');
const fs = require('fs');
const bodyParser = require('body-parser')
const app = express();
const port = 3000;

app.use(bodyParser());

app.use('/', express.static(__dirname));
http.createServer(app).listen(port);


app.post('/', function (req, resp) {
  resp.end(JSON.stringify(req.body));
})
