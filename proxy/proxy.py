# -*- coding:utf-8 -*-
import sys
import json
import socket
import select
from cache import Cache
from urlparse import urlparse


class Proxy(object):
    """
    支持http协议的代理服务 （暂不支持https）
    """
    BUFFER_SIZE = 2048
    HTTP_METHOD = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
    HTTPS_METHOD = ['CONNECT']

    def __init__(self, server_sock):
        self.client_sock, (self.client_ip, self.client_port) = server_sock.accept()

    def parse_method(self):

        self.request = self.client_sock.recv(self.BUFFER_SIZE)  # 获取HTTP请求报文

        if not self.request:                              # 未获取报文直接返回
            return

        # print self.request
        lines = self.request.split('\r\n')
        self.method = lines[0].split()[0]          # 解析method，区分协议

    def run(self):
        self.parse_method()
        if self.request:
            if self.method in self.HTTP_METHOD:
                self.http_request()
            elif self.method in self.HTTPS_METHOD:
                self.https_request()

    def http_request(self):

        self.parse_url_http()

        # 判断是否在防火墙里
        if not self.filter_fire_wall():

            # 确认该host和port可连接
            try:
                addr_info = socket.getaddrinfo(self.host, self.port)[0]
            except socket.gaierror, e:
                print 'This site have error!!!!'
                print 'The host is ' + self.host
                print 'The port is ' + str(self.port)
                print 'The url is ' + self.url
                print 'The address information is ' + addr_info
                sys.exit(1)
            else:
                # 对目标服务器建立socket连接
                self.target_sock = socket.socket(addr_info[0], 1)
                self.target_sock.connect(addr_info[4])
                self.target_sock.send(self.request)
                self.return_data()

    def parse_url_http(self):

        lines = self.request.split('\r\n')
        self.url = lines[0].split()[1]

        parse_url = urlparse(self.url)
        self.host = parse_url.netloc
        self.path = parse_url.path

        if ':' in self.host:             # 处理url附带端口的情况
            self.port = self.host.split(':')[1]
            self.host = self.host.split(':')[0]
        else:
            self.port = 80               # http协议默认端口为80

        print self.method, self.url
        # print self.host, self.client_ip

    def https_request(self):
        pass

    def return_data(self):

        cache = Cache(url=self.url)

        if cache.is_cache_exist():
            print 'Cache Successful!!!'

        inputs = [self.target_sock, self.client_sock]

        fish_data = self.fish()
        # 判断是否为钓鱼网站
        if fish_data:
            self.client_sock.send(fish_data)
        else:
            while True:
                # 监控可读的socket对象, 利用select实现非阻塞读取
                readable, writeable, errors = select.select(inputs, [], inputs, 3)

                # 存在错误则直接退出
                if errors:
                    break

                last_url = ''
                # 建立过tcp连接后则直接交换客户端和目标服务器的数据
                for socket in readable:
                    data = socket.recv(self.BUFFER_SIZE)
                    if data:
                        if socket is self.target_sock:
                            self.client_sock.send(data)
                            cache.update_cache(data)
                        elif socket is self.client_sock:
                            self.target_sock.send(data)
                    else:
                        break

        # 无数据传输后关闭socket连接
        self.client_sock.close()
        self.target_sock.close()

    def filter_fire_wall(self):
        # 防火墙，限制用户ip以及访问的网站

        with open('filter.json', 'r') as f:
            filter_json = json.load(f)

            if self.client_ip in filter_json['ip']:
                print 'Filter client ip %s.' % self.client_ip
                return True

            for filter_host in filter_json['host']:
                if self.host.endswith(filter_host):
                    print 'Filter host %s.' % filter_host
                    return True

        return False

    def fish(self):

        # 钓鱼网站
        with open('filter.json', 'r') as f:

            filter_json = json.load(f)

            for fish in filter_json['fishing']:
                if self.host == fish and self.path == '/':

                    # 返回重定向相应
                    return str('HTTP/1.1 302 Moved Temporarily\r\nLocation: http://' + \
                    filter_json['fishing'][self.host] + '\r\n\r\n')

        return False