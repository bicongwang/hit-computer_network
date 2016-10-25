# -*- coding:utf-8 -*-
import socket
from global_data import *

# 设置网络连接为ipv4， 传输层协议为udp
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 传输完成后立即回收该端口
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 任意ip均可以访问
s.bind(('', SERVER_PORT))

pull_data(s)