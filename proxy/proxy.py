# -*- coding:utf-8 -*-
import sys
import json
import socket
import select
from urlparse import urlparse


class Proxy(object):
    """
    支持http协议的代理服务 （暂不支持https）
    """
    BUFFER_SIZE = 4096
    HTTP_METHOD = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
    HTTPS_METHOD = ['CONNECT']

    def __init__(self, server):
        self.client, (self.client_ip, self.client_port) = server.accept()

    def parse_method(self):
        self.request = self.client.recv(self.BUFFER_SIZE)

        if not self.request:
            return

        # print self.request
        lines = self.request.split('\r\n')                # 解析html协议的各行

        self.method = lines[0].split()[0]
        self.url = lines[0].split()[1]


    def run(self):
        self.parse_method()
        if self.request:
            if self.method in self.HTTP_METHOD:
                self.http_request()
            elif self.method in self.HTTPS_METHOD:
                self.https_request()

    def http_request(self):

        self.parse_url_http()

        if not self.filter_fire_wall():

            del_url = self.scheme + '://' + self.host
            request = self.request.replace(del_url, '')
            # print request

            try:
                addr_info = socket.getaddrinfo(self.host, self.port)[0]
            except socket.gaierror, e:
                print 'This site have error!!!!'
                print 'The host is' + self.host
                print 'The port is' + self.port
                print 'The url is' + self.url
                print 'The address information is' + addr_info
                sys.exit(1)
            else:
                self.target = socket.socket(addr_info[0], addr_info[1])
                self.target.connect(addr_info[4])
                self.target.send(self.request)
                self.return_data()

    def parse_url_http(self):
        parse_url = urlparse(self.url)
        self.host = parse_url.netloc
        self.scheme = parse_url.scheme

        if ':' in self.host:
            self.port = self.host.split(':')[1]
            self.host = self.host.split(':')[0]
        else:
            self.port = 80

            # print self.method, self.url
            print self.host, self.client_ip

    def https_request(self):
        pass

    def return_data(self):
        inputs = [self.client, self.target]
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

    def filter_fire_wall(self):

        with open('filter.json', 'r') as f:
            filter_json = json.load(f)

            if self.client_ip in filter_json['ip']:
                print 'Filter client ip.'
                return True

            for filter_host in filter_json['host']:
                if self.host.endswith(filter_host):
                    print 'Filter host.'
                    return True

        return False

class Client(object):
    pass

