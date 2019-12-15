const express = require('express');
const http = require('http');
const fs = require('fs');
const url = require('url');
const bodyParser = require('body-parser')
const app = express();
const port = 3000;

badSites=[]

app.use(bodyParser());

app.use('/', express.static(__dirname));
http.createServer(app).listen(port);


// app.get('/', function (req, res) {
//   res.render('form-inline');
//   res.sendFile('index.html');
//   console.log(url.parse(req.body.link).host);
// })

app.post('/',function(req,res){
  var link = url.parse(req.body.link).host;
  badSites.push(link);
  res.send('Test: ' +link);
  console.log(badSites);
});