# -*- coding:utf-8 -*-
import socket
import select


class Proxy(object):
    """
    支持http协议的代理服务 （暂不支持https）
    """
    BUFFER_SIZE = 4096
    HTTP_METHOD = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
    HTTPS_METHOD = ['CONNECT']

    def __init__(self, server):
        self.client, _ = server.accept()

    def parse_request(self):
        self.request = self.client.recv(self.BUFFER_SIZE)

        if not self.request:
            return

        # print self.request
        lines = self.request.split('\r\n')                # 解析html协议的各行

        self.method = lines[0].split()[0]
        self.url = lines[0].split()[1]
        self.host = lines[1].split()[1]

        if len(self.url.split(':')) > 2:
            self.port = self.url.split(':')[2]
        else:
            self.port = 80

        print self.method, self.url, self.host, self.port

    def run(self):
        self.parse_request()
        if self.request:
            if self.method in self.HTTP_METHOD:
                self.http_request()
            elif self.method in self.HTTPS_METHOD:
                self.https_request()

    def http_request(self):
        del_url = 'http://' + self.host
        request = self.request.replace(del_url, '')
        # print request

        addr_info = socket.getaddrinfo(self.host, self.port)[0]
        self.target = socket.socket(addr_info[0], addr_info[1])
        self.target.connect(addr_info[4])
        self.target.send(request)
        self.return_data()

    def https_request(self):
        pass

    def return_data(self):
        inputs=[self.client, self.target]
        while True:
            readable, writeable, errs=select.select(inputs, [], inputs, 3)
            if errs:
                break
            for socket in readable:
                data=socket.recv(self.BUFFER_SIZE)
                if data:
                    if socket is self.client:
                        self.target.send(data)
                    elif socket is self.target:
                        self.client.send(data)
                else:
                    break
        self.client.close()
        self.target.close()


class Client(object):
    pass

