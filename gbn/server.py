# -*- coding:utf-8 -*-
import socket
import thread
import client
from util import *


def new_server_socket(server_port, client_port, path, protocol):
    # 设置网络连接为ipv4， 传输层协议为udp
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 传输完成后立即回收该端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 任意ip均可以访问
    s.bind(('', server_port))

    p = protocol(s)
    p.push_data(path, client_port)


if __name__ == '__main__':

    thread.start_new_thread(new_server_socket, (SERVER_PORT, CLIENT_PORT, 'data/server_push.txt', Sr))

    # new_server_socket(SERVER_PORT, CLIENT_PORT, 'data/server_push.txt', Sr)
    client.new_client_socket(CLIENT_PORT_EXTRA, Gbn)

