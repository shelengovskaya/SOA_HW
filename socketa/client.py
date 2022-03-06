import socket
import sys


if __name__=='__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 9093)
    sock.connect(server_address)
    print('Connection opened.')

    nickname = input('Your nickname: ')

    try:

        while True:
       
            message = input('{} > '.format(nickname))
            sock.sendall(message.encode())

            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(1024)
                amount_received += len(data)
                print('SERVER > {}'.format(data.decode()))


    except KeyboardInterrupt:
        sock.close()
        print('\nConnection closed.')
