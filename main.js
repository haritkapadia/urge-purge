#!/bin/node
const httpProxy = require("http-proxy");
const http = require("http");
const url = require("url");
const net = require('net');
const child_process = require('child_process');
const readline = require('readline');
const request = require('request');

const badSites = [
    {'www.youtube.com': 10},
    {'www.reddit.com': 10},
    {'www.instagram.com': 10}
];

const removedSites = [];

const transform = (arr) => {
    const out = [];
    for(let i = 0; i < arr.length; i++) {
        out.push(Object.keys(arr[i])[0]);
    }
    return out;
};

const platform = child_process.spawn('python', ['main.py']);
platform.stdout.on('data', (data) => {
    const cmd = data.toString().trim().split(' ');
    if(cmd[0] == 'site') {
        if(cmd[1] == 'remove') {
            const pos = transform(badSites).indexOf(cmd[2]);
            removedSites.push(badSites[pos]);
        } else if(cmd[1] == 'add') {
            const pos = transform(badSites).indexOf(cmd[2]);
            removedSites.push(badSites[pos]);
            removedSites.filter(e => e != badSites[pos]);
        }
    }
    console.log(cmd);
});
platform.stderr.on('data', (data) => {
    console.error(data.toString());
});
const message = 'site set ' + badSites.map((o) => {
    const key = Object.keys(o)[0];
    return key + ' ' + o[key];
}).join(' ') + '\n';
platform.stdin.write(message, (err) => {
    if(err)
        throw err;
    console.log("We in!");
});

var server = http.createServer(function (req, res) {
    var urlObj = url.parse(req.url);

    console.log("Proxy HTTP request for:", urlObj.host);
    if(transform(badSites).indexOf(urlObj.host) != -1 && transform(removedSites).indexOf(urlObj.host) == -1) {
        platform.stdin.write('site block ' + urlObj.host + '\n', (err) => {
            if(err)
                throw err;
        });
        res.end();
        return;
    } else {
        var proxy = httpProxy.createProxyServer({});
        proxy.on('error', (err, req, res) => {
            console.log("proxy error", err);
            res.end();
        });
        
        var target = urlObj.protocol + "//" + urlObj.host;
        proxy.web(req, res, {target: target});
    }
}).listen(1080);  //this is the port your clients will connect to

var regex_hostport = /^([^:]+)(:([0-9]+))?$/;

var getHostPortFromString = function (hostString, defaultPort) {
    var host = hostString;
    var port = defaultPort;

    var result = regex_hostport.exec(hostString);
    if (result != null) {
        host = result[1];
        if (result[2] != null) {
            port = result[3];
        }
    }

    return ( [host, port] );
};

server.addListener('connect', function (req, socket, bodyhead) {
    var hostPort = getHostPortFromString(req.url, 443);
    var hostDomain = hostPort[0];
    var port = parseInt(hostPort[1]);
    console.log("Proxying HTTPS request for:", hostDomain, transform(badSites), transform(badSites).indexOf(hostDomain), transform(removedSites), transform(removedSites).indexOf(hostDomain));
    if(transform(badSites).indexOf(hostDomain) != -1 && transform(removedSites).indexOf(hostDomain) == -1) {
        platform.stdin.write('site block ' + hostDomain + '\n', (err) => {
            if(err)
                throw err;
        });
    } else {
        var proxySocket = new net.Socket();
        proxySocket.connect(port, hostDomain, () => {
            proxySocket.write(bodyhead);
            socket.write("HTTP/" +
                         req.httpVersion +
                         " 200 Connection established\r\n\r\n");
        });

        proxySocket.on('data', (chunk) => {
            socket.write(chunk);
        });
        proxySocket.on('end', () => {
            socket.end();
        });
        proxySocket.on('error', () => {
            socket.write("HTTP/" + req.httpVersion + " 500 Connection error\r\n\r\n");
            socket.end();
        });
        socket.on('data', (chunk) => {
            proxySocket.write(chunk);
        });
        socket.on('end', () => {
            proxySocket.end();
        });

        socket.on('error', () => {
            proxySocket.end();
        });
    }
});
