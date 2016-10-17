# -*- coding:utf-8 -*-
import socket
import thread
from proxy import Proxy

PORT = 5000
THREAD = 10

if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', PORT))
    server.listen(THREAD)

    while 1:
        # print 'Create new thread.\n'
        thread.start_new_thread(Proxy(server).run, ())