# -*- coding: utf-8 -*-

import multiprocessing
import socket
import time


class HttpProxy(object):
    """http proxy"""

    def __init__(self, host, port):
        self.addr = (host, port)

    def run(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy.bind(self.addr)
        proxy.listen(5)

        process_list = []

        """ prefork """
        for i in range(4):
            process = multiprocessing.Process(target=HttpProxy.worker, args=(proxy,))
            process.daemon = True
            process.start()
            process_list.append(process)

        for p in process_list:
            p.join()

    @classmethod
    def recv_timeout(cls, sock, timeout=2):
        sock.setblocking(0)

        begin = time.time()
        data = ''

        while True:
            if len(data) != 0 and time.time() - begin > timeout:
                break
            elif time.time() - begin > 2 * timeout:
                break

            try:
                ret = sock.recv(8192)
                if ret:
                    data += ret
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass

        return data

    @classmethod
    def forward(cls, client, src, method, header_dict=None, params=''):
        try:
            host = socket.gethostbyname(header_dict['Host'])
        except:
            return
        port = 80

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, port))

        if method == 'HEAD':
            pass
        elif method == 'GET':
            header = 'GET {} HTTP/1.1\r\n'.format(src)
            for key in header_dict:
                header += '{}: {}\r\n'.format(key, header_dict[key])
            header += '\r\n'
            server.sendall(header)

            client.sendall(cls.recv_timeout(server))

        elif method == 'POST':
            pass

        server.close()

    @classmethod
    def worker(cls, proxy):
        while True:
            client, addr = proxy.accept()
            request = cls.recv_timeout(client, 1)
            if len(request) == 0:
                client.close()
                continue

            print addr
            print request

            method, src, proto = request.split('\r\n')[0].split(' ')

            if 'http' in src:
                scheme = 'http'
            elif '443' in src:
                scheme = 'https'
            if scheme == 'https':
                client.close()
                continue

            header_dict = {}
            for header in request.split('\r\n')[1:]:
                if len(header) != 0:
                    header_dict[header.split(':')[0]] = header.split(':')[1].strip(' ')

            if header_dict.has_key('Proxy-Connection'):
                header_dict.pop('Proxy-Connection')
            header_dict['User-Agent'] = 'HttpProxy'

            cls.forward(client, src, method, header_dict)
            client.close()


if __name__ == '__main__':
    HttpProxy('127.0.0.1', 1234).run()
