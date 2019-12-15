const express = require('express');
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

let badSites = JSON.parse(fs.readFileSync('sites.json').toString('utf8'));
let badPrograms = JSON.parse(fs.readFileSync('desktop.json').toString('utf8'));

app.use(bodyParser());

app.use('/', express.static(__dirname));
http.createServer(app).listen(port);


app.get('/sites.json', function (req, res) {
  res.end(JSON.stringify(badSites));
})

app.post('/sites.html',function(req,res){
    badSites = Array.from(new Set(Object.keys(req.body).map((ll) => {
      return url.parse(ll).hostname;
    })));

    fs.writeFile('sites.json', JSON.stringify(badSites), (err) => {
        if(err)
            throw err;
    }); 
    console.log();
  res.redirect('/sites.html');
  console.log(badSites);
});

app.get('/desktop.json', function (req, res) {
  res.end(JSON.stringify(badPrograms));
});

app.post('/desktop.html',function(req,res) {
    badPrograms = Array.from(new Set(Object.keys(req.body)));
    fs.writeFile('desktop.json', JSON.stringify(badPrograms), (err) => {
        if(err)
            throw err;
    }); 
    console.log();
    res.redirect('/desktop.html');
    console.log(badPrograms);
});

