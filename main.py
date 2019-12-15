#!/bin/env python

import os
import psutil
import requests
import signal
import socket
import sys
import threading
import traceback
from urllib import parse

kill_list = {'vi', 'geeqie', 'jupyter-console'}

current = set(psutil.process_iter())
def kill_bad_processes(current,
                       kill_list,
                       global_blacklist={'flake8',
                                         'emacs',
                                         'systemd',
                                         'firefox'}):
    previous = current
    current = set(psutil.process_iter())
    _a = current - previous
    if len(_a) != 0:
        for a in _a:
            if a.name() not in global_blacklist and a.name() in kill_list:
                print(a.name(), flush=True)
                a.kill()
    return current;


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

try:
    i = 0
    while True:
        prev = current
        current = kill_bad_processes(current, kill_list)
        """
        if prev != current:
            i += 1
        if i > 3:
            break
        """
except KeyboardInterrupt:
    pass
