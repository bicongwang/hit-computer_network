import select

SERVER_HOST = '127.0.0.1'
CLIENT_HOST = '127.0.0.1'

SERVER_PORT = 5001
CLIENT_PORT = 5002

BUFFER_SIZE = 2048

WINDOWS = 8
SEQ_LENGTH = 18

MAX_TIME = 3


class Data(object):

    seq = 0

    def __init__(self, msg, state=False):
        self.msg = msg
        self.state = state
        self.seq = str(Data.seq)
        Data.seq = (Data.seq + 1) % SEQ_LENGTH

    def __str__(self):
        return self.seq + ' ' + self.msg


def push_data(s, path):

    time = 0

    data_windows = []

    with open(path, 'r') as f:

        while True:

            if time > MAX_TIME:
                for data in data_windows:
                    data.state = False

            while len(data_windows) < WINDOWS:
                line = f.readline().strip()

                if not line:
                    break

                data = Data(line)
                data_windows.append(data)

            for data in data_windows:
                if not data.state:
                    s.sendto(str(data), (SERVER_HOST, SERVER_PORT))
                    data.state = True

            readable, writeable, errors = select.select([s, ], [], [], 1)

            if not data_windows:
                break


            if len(readable) > 0:
                message, address = s.recvfrom(BUFFER_SIZE)
                print 'ACK ' + message
                time = 0

                if int(message) >= int(data_windows[0].seq):

                    while len(data_windows):

                        if data_windows[0].seq == message:
                            data_windows.pop(0)
                            break

                        data_windows.pop(0)

            time += 1

    s.close()


def pull_data(s):

    lose_pkg_index = 0

    last_ack = SEQ_LENGTH - 1

    get_data = []
    time = 0

    while 1:

        readable, writeable, errors = select.select([s, ], [], [], 2)

        time += 1

        if len(readable) > 0:
            message, address = s.recvfrom(BUFFER_SIZE)
            ack = int(message.split()[0])
            if last_ack == (ack - 1) % SEQ_LENGTH:

                lose_pkg_index += 1

                if lose_pkg_index % 5 == 3:
                    continue

                s.sendto(str(ack), address)
                last_ack = ack
                # print message.split()[1]
                if message.split()[1] not in get_data:
                    get_data.append({message.split()[1]: message.split()[1]})
                    print message
            else:
                s.sendto(str(last_ack), address)

            time = 0

        # if time > MAX_TIME:
        #     break

    s.close()