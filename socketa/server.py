import socket
import sys

import threading


def get_client_message(connection, addr):

    while True:
        try:
            data = connection.recv(1024)
            print('received {}'.format(data))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no data from', addr)
                break

        except:
            connection.close()


if __name__=='__main__':


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 9093)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    sock.listen()
        

    while True:
        connection, addr = sock.accept()
        print('connection from', addr)

        threading.Thread(target=get_client_message, args=(connection, addr,)).start()
