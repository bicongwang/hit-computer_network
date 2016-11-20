# -*- coding:utf-8 -*-
import socket
import thread
import server

from util import *


def new_client_socket(client_port, protocol):
    # 设置网络连接为ipv4， 传输层协议为tcp
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 传输完成后立即回收该端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 任意ip均可以访问
    s.bind(('', client_port))

    p = protocol(s)
    p.pull_data()


if __name__ == '__main__':

    # 接收方开启多线程
    thread.start_new_thread(server.new_server_socket, (SERVER_PORT_EXTRA, CLIENT_PORT_EXTRA, 'data/client_push.txt', Gbn))

    # server.new_server_socket(SERVER_PORT_EXTRA, CLIENT_PORT_EXTRA, 'data/client_push.txt', Gbn)
    new_client_socket(CLIENT_PORT, Sr)

