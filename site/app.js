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
});

app.post('/sites.html',function(req,res){
  
    badSites = Array.from(new Set(Object.keys(req.body).map((ll) => {
      // console.log(url.parse(ll));
      let name = url.parse(ll).hostname;
      if(name === null)
        name = ll;
      // console.log("body: "+req.body);
      // console.log("hours: "+req.body[ll][0]);
      // console.log("minutes: "+req.body[ll][1]);
      // console.log("seconds: "+req.body[ll][2]);
      let seconds = (parseInt(req.body[ll][0])*3600 + parseInt(req.body[ll][1])*60 + parseInt(req.body[ll][2]));
      if(isNaN(seconds))
        seconds = 0;
      // console.log('badSites map', ll, name, seconds);
      return JSON.parse('{"'+name+'":'+seconds+'}');
    })));
    fs.writeFile('sites.json', JSON.stringify(badSites), (err) => {
        if(err)
            throw err;
    }); 
  res.redirect('/sites.html');
  // console.log(badSites);
});

app.get('/desktop.json', function (req, res) {
  res.end(JSON.stringify(badPrograms));
});

app.post('/desktop.html',function(req,res) {
    badPrograms = Array.from(new Set(Object.keys(req.body).map((ll) => {
      // console.log(url.parse(ll));
      let name = ll;
      console.log("body: ");
      for(const ee in req.body)
        console.log(ee);
      if(req.body[ll][0] == '')
        req.body[ll][0] = 0;
      if(req.body[ll][1] == '')
        req.body[ll][1] = 0;
      if(req.body[ll][2] == '')
        req.body[ll][2] = 0;              
      console.log("hours: "+req.body[ll][0]);
      console.log("minutes: "+req.body[ll][1]);
      console.log("seconds: "+req.body[ll][2]);
      let seconds = (parseInt(req.body[ll][0])*3600 + parseInt(req.body[ll][1])*60 + parseInt(req.body[ll][2]));
      // if(isNaN(seconds))
      //   seconds = 0;
      // console.log('badSites map', ll, name, seconds);
      return JSON.parse('{"'+name+'":'+seconds+'}');
    })));
    fs.writeFile('desktop.json', JSON.stringify(badPrograms), (err) => {
        if(err)
            throw err;
    }); 
  res.redirect('/desktop.html');
  // console.log(badSites);
});

