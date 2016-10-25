# -*- coding:utf-8 -*-
import os
import socket
import thread
from proxy import Proxy

PORT = 5000
THREAD = 5

def check_exist_cache_dir():
    # 创建缓存目录
    if not os.path.exists('./cache'):
        os.mkdir('./cache')

if __name__ == '__main__':

    # 设置网络连接为ipv4， 传输层协议为tcp
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 传输完成后立即回收该端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 任意ip均可以访问
    s.bind(('', PORT))
    # 控制队列中可等待的最大链接
    s.listen(THREAD)

    check_exist_cache_dir()

    while 1:
        # print 'Create new thread.\n'
        thread.start_new_thread(Proxy(s).run, ())