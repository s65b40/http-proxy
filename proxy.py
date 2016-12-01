# -*- coding: utf-8 -*-

import logging
import multiprocessing
import socket

import requests

host = '127.0.0.1'
port = 1234


def log(msg):
    pass


def forward(conn, addr):
    pass


def worker(s):
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)

        method, src, proto = request.split('\r\n')[0].split(' ')
        if 'http' in src:
            scheme = 'http'
        elif '443' in src:
            scheme = 'https'
        headers = {}
        for header in request.split('\r\n')[1:]:
            if len(header) != 0:
                headers[header.split(':')[0]] = header.split(':')[1].strip(' ')

        print request
        print method
        print src
        print scheme
        print headers

        if scheme == 'https':
            logging.debug('https unsupported!')
            conn.close()

        if method == 'GET':
            rsp = requests.get(src)
            if rsp.status_code != 200:
                conn.sendall('Request Error')
            else:
                conn.sendall(rsp.content)

        conn.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)

process_list = []

""" prefork """
for i in range(4):
    process = multiprocessing.Process(target=worker, args=(s,))
    process.daemon = True
    process.start()
    process_list.append(process)

for p in process_list:
    p.join()
