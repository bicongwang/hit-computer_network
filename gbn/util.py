# -*- coding:utf-8 -*-
import sys
import select
from random import random

# 设置在localhost进行测试
HOST = '127.0.0.1'

# 设置服务器端与客户端的端口号
SERVER_PORT = 5001
CLIENT_PORT = 5002

# 另开端口组实现双向通信
SERVER_PORT_EXTRA = 5003
CLIENT_PORT_EXTRA = 5004

# 单次读取的最大字节数
BUFFER_SIZE = 2048

# 窗口与包序号长度
WINDOWS_LENGTH = 8
SEQ_LENGTH = 10

# 最大延迟时间
MAX_TIME = 3


class Data(object):

    def __init__(self, msg, seq=0, state=0):
        self.msg = msg
        self.state = state
        self.seq = str(seq % SEQ_LENGTH)

    def __str__(self):
        return self.seq + ' ' + self.msg


class Gbn(object):

    def __init__(self, s):
        self.s = s

    def push_data(self, path, port):

        # 计时和包序号初始化
        time = 0
        seq = 0

        data_windows = []

        with open(path, 'r') as f:

            while True:

                # 当超时后，将窗口内的数据更改为未发送状态
                if time > MAX_TIME:
                    for data in data_windows:
                        data.state = 0

                # 窗口中数据少于最大容量时，尝试添加新数据
                while len(data_windows) < WINDOWS_LENGTH:
                    line = f.readline().strip()

                    if not line:
                        break

                    data = Data(line, seq=seq)
                    data_windows.append(data)
                    seq += 1

                # 窗口内无数据则退出总循环
                if not data_windows:
                    break

                # 遍历窗口内数据，如果存在未成功发送的则发送
                for data in data_windows:
                    if not data.state:
                        self.s.sendto(str(data), (HOST, port))
                        data.state = 1

                # 无阻塞socket连接监控
                readable, writeable, errors = select.select([self.s, ], [], [], 1)

                if len(readable) > 0:

                    # 收到数据则重新计时
                    time = 0

                    message, address = self.s.recvfrom(BUFFER_SIZE)
                    sys.stdout.write('ACK ' + message + '\n')

                    for i in range(len(data_windows)):
                        if message == data_windows[i].seq:
                            data_windows = data_windows[i+1:]
                            break
                else:
                    # 未收到数据则计时器加一
                    time += 1

        self.s.close()

    def pull_data(self):

        # 记录上一个回执的ack的值
        last_ack = SEQ_LENGTH - 1

        data_windows = []

        while True:

            readable, writeable, errors = select.select([self.s, ], [], [], 1)

            if len(readable) > 0:
                message, address = self.s.recvfrom(BUFFER_SIZE)

                ack = int(message.split()[0])

                # 连续接收数据则反馈当前ack
                if last_ack == (ack - 1) % SEQ_LENGTH:

                    # 丢包率为0.2
                    if random() < 0.2:
                        continue

                    self.s.sendto(str(ack), address)
                    last_ack = ack

                    # 判断数据是否重复
                    if ack not in data_windows:
                        data_windows.append(ack)
                        sys.stdout.write(message + '\n')

                    while len(data_windows) > WINDOWS_LENGTH:
                        data_windows.pop(0)
                else:
                    self.s.sendto(str(last_ack), address)

        self.s.close()


class Sr(object):

    def __init__(self, s):
        self.s = s

    def push_data(self, path, port):

        # 计时和包序号初始化
        time = 0
        seq = 0

        data_windows = []

        with open(path, 'r') as f:

            while True:

                # 当超时后，将窗口内第一个发送成功未确认的数据状态更改为未发送
                if time > MAX_TIME:
                    for data in data_windows:
                        if data.state == 1:
                            data.state = 0
                            break

                # 窗口中数据少于最大容量时，尝试添加新数据
                while len(data_windows) < WINDOWS_LENGTH:
                    line = f.readline().strip()

                    if not line:
                        break

                    data = Data(line, seq=seq)
                    data_windows.append(data)
                    seq += 1

                # 窗口内无数据则退出总循环
                if not data_windows:
                    break

                # 遍历窗口内数据，如果存在未成功发送的则发送
                for data in data_windows:
                    if not data.state:
                        self.s.sendto(str(data), (HOST, port))
                        data.state = 1

                readable, writeable, errors = select.select([self.s, ], [], [], 1)

                if len(readable) > 0:

                    # 收到数据则重新计时
                    time = 0

                    message, address = self.s.recvfrom(BUFFER_SIZE)
                    sys.stdout.write('ACK ' + message + '\n')

                    # 收到数据后更改该数据包状态为已接收
                    for data in data_windows:
                        if message == data.seq:
                            data.state = 2
                            break
                else:
                    # 未收到数据则计时器加一
                    time += 1

                # 当窗口中首个数据已接收时，窗口前移
                while data_windows[0].state == 2:
                    data_windows.pop(0)

                    if not data_windows:
                        break

        self.s.close()

    def pull_data(self):

        # 窗口的初始序号
        seq = 0
        data_windows = {}

        while True:

            readable, writeable, errors = select.select([self.s, ], [], [], 1)

            if len(readable) > 0:
                message, address = self.s.recvfrom(BUFFER_SIZE)

                ack = message.split()[0]

                # 丢包率为0.2
                if random() < 0.2:
                    continue

                # 返回成功接收的包序号
                self.s.sendto(ack, address)
                data_windows[ack] = message.split()[1]

                # 滑动窗口
                while str(seq) in data_windows:
                    sys.stdout.write(str(seq) + ' ' + data_windows[str(seq)] + '\n')
                    data_windows.pop(str(seq))
                    seq = (seq + 1) % SEQ_LENGTH

        self.s.close()

