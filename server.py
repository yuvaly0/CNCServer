import socket
import select
from datetime import datetime
import time
from communication import decode_header, decode_message, encode_message, format_timestamp, MESSAGES

host = '0.0.0.0'
port = 65432
HEADER_SIZE = 4

# todo add magic number to verify integrrity
# todo, add some unique id to each client
'''
protocol
[header] - 4 bytes that represent the length of the message to come
[message] - 'header' length bytes that contains the command
    - command
'''

# todo: move to class
last_ping_time = {}


def handle_recv_msg(current_socket):
    try:
        encoded_header = current_socket.recv(HEADER_SIZE)
        if not encoded_header:
            print("Client closed connection")
            # throw instead of returning boolean
            return False, current_socket

        message_length = decode_header(encoded_header)

        if message_length == -1:
            return False, current_socket

        sent_timestamp, message = decode_message(current_socket.recv(message_length))

        now = format_timestamp(datetime.now())
        delta_ms = (now - sent_timestamp).total_seconds() * 1000

        if sent_timestamp is None:
            return False, current_socket

        print(f'[RECEIVED] {datetime.now()} - {current_socket.fileno()} - {message} - took {delta_ms}ms')
        return True, current_socket
    except ConnectionResetError as e:
        print(f'[RECEIVED] {current_socket.fileno()} - disconnected forcibly')
        return False, current_socket


def handle_send_msg(current_socket, message_queues):
    current_msg = message_queues[current_socket]
    current_time = datetime.now()

    print(f'[SENDING] {current_time} - {current_socket.fileno()} - {current_msg}')

    current_socket.sendall(encode_message(current_msg))


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)
        print(f"Server listening on {host}:{port}")

        inputs = [server_socket]
        outputs = []

        message_queues = {}

        while True:
            readable, writeable, exceptional = select.select(inputs, outputs, inputs + outputs)

            current_time = time.time()

            for current_socket in readable:
                if current_socket is server_socket:
                    print('[+] Received new connection')
                    connection, client_address = server_socket.accept()
                    connection.setblocking(False)
                    inputs.append(connection)
                    outputs.append(connection)

                    message_queues[connection] = MESSAGES.get('PING')
                    last_ping_time[connection] = current_time
                else:
                    # todo: current_socket is patch
                    result, current_socket = handle_recv_msg(current_socket)

                    if not result:
                        print(f'[RECEIVED] {datetime.now()} - {current_socket.fileno()} - BAD MESSAGE')
                        inputs.remove(current_socket)
                        outputs.remove(current_socket)
                        current_socket.close()

            for current_socket in writeable:
                try:
                    if message_queues.get(current_socket, None):
                        handle_send_msg(current_socket, message_queues)
                        del message_queues[current_socket]
                except Exception as e:
                    print(f'could not send message to client {e}')
                    pass

            for current_socket in exceptional:
                # todo: create one function to handle cleanup logic
                print(f'Exception socket - {current_socket} removed')
                inputs.remove(current_socket)
                outputs.remove(current_socket)

                current_socket.close()

            for current_socket in inputs:
                if current_socket is not server_socket and current_time - last_ping_time[current_socket] >= 5:
                    message_queues[current_socket] = MESSAGES.get('PING')
                    last_ping_time[current_socket] = current_time


start_server()
