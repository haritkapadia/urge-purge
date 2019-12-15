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


app.get('/sites.json', function (req, res) {
  res.end(JSON.stringify(badSites));
})

app.post('/sites.html',function(req,res){
  var link = url.parse(req.body.link).host;
  if(link != null && link.length>0){  
    badSites.push(link);
  }
  res.redirect('/sites.html');
  console.log(badSites);
});
