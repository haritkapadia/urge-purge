#!/bin/node
const httpProxy = require("http-proxy");
const http = require("http");
const url = require("url");
const net = require('net');
const child_process = require('child_process');
const readline = require('readline');

const badSites = [
    'www.youtube.com',
    'www.reddit.com',
    'www.instagram.com'
];

process.stdin.on('data', (data) => {
    console.log('Killed:', String(data));
});

var server = http.createServer(function (req, res) {
    var urlObj = url.parse(req.url);
    var target = urlObj.protocol + "//" + urlObj.host;

    console.log("Proxy HTTP request for:", urlObj.host);
    if(badSites.includes(urlObj.host)) {
        console.log("NO ME");
        res.end();
        return;
    }

    var proxy = httpProxy.createProxyServer({});
    proxy.on('error', (err, req, res) => {
        console.log("proxy error", err);
        res.end();
    });

    proxy.web(req, res, {target: target});
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
    console.log("Proxying HTTPS request for:", hostDomain, port);

    var proxySocket = new net.Socket();
    proxySocket.connect(port, hostDomain, function () {
        proxySocket.write(bodyhead);
        socket.write("HTTP/" + req.httpVersion + " 200 Connection established\r\n\r\n");
    });

    proxySocket.on('data', function (chunk) {
        socket.write(chunk);
    });
    proxySocket.on('end', function () {
        socket.end();
    });
    proxySocket.on('error', function () {
        socket.write("HTTP/" + req.httpVersion + " 500 Connection error\r\n\r\n");
        socket.end();
    });
    socket.on('data', function (chunk) {
        proxySocket.write(chunk);
    });
    socket.on('end', function () {
        proxySocket.end();
    });

    socket.on('error', function () {
        proxySocket.end();
    });

});
