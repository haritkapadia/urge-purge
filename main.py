#!/bin/env python

import flask
import os
import proxy
import psutil
import requests
import signal
import socket
import sys
import threading
import traceback
from urllib import parse

kill_list = {'vi'}

current = set(psutil.process_iter())
def kill_bad_processes(current,
                       kill_list,
                       global_blacklist={'flake8', 'emacs', 'systemd'}):
    previous = current
    current = set(psutil.process_iter())
    _a = current - previous
    if len(_a) != 0:
        for a in _a:
            print(a.name(), a.pid, a.parents())
            if a.name() not in global_blacklist and a.name() in kill_list:
                a.kill()


def proxy_thread(conn, client_addr):
    MAX_IN_DATA = 4096
    request = conn.recv(MAX_IN_DATA)
    first_line = request.decode().split('\n')[0]
    rest_type, url = first_line.split(' ')[:2]
    url_obj = parse.urlparse(url)
    r = requests.get(url)
    try:
        conn.send(request)
        conn.sendall(r.content)
    except:
        print(traceback.format_exc())
        conn.close()
        

def server():
    BACKLOG = 50
    host = 'localhost'
    port = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(BACKLOG)

    try:
        while True:
            conn, client_addr = s.accept()
            print(conn, client_addr)
            proxy_thread(conn, client_addr)
            conn.close()
    except:
        print(traceback.format_exc())
        s.close()

server()
print('DIE')
