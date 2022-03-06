import socket
import sys

import threading

all_connections = []


def get_client_message(connection, addr):

    while True:
        try:
            data = connection.recv(1024)

            if data:
                connection.sendall(data)
            else:
                break

        except:
            all_connections.remove(addr)

            print('All connections:', end=' ')
            for c in all_connections:
                print(c, end=' ')
            print()

            connection.close()


if __name__=='__main__':


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 9095)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    sock.listen()
        

    while True:
        connection, addr = sock.accept()
        print('Connection from', addr)


        all_connections.append(addr)

        print('All connections:', end=' ')
        for c in all_connections:
            print(c, end=' ')
        print()

        threading.Thread(target=get_client_message, args=(connection, addr,)).start()
