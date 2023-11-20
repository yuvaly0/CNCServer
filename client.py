import socket
from communication import encode_message, decode_header, decode_message, MESSAGES

HOST = '127.0.0.1'
PORT = 65432

HEADER_SIZE = 4

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    while True:
        encoded_header = client_socket.recv(HEADER_SIZE)
        if not encoded_header:
            print("Server closed the connection")
            break
        else:
            message_length = decode_header(encoded_header)
            decoded_message = decode_message(client_socket.recv(message_length))

            print(f'Client received {decoded_message}')
            if decoded_message == MESSAGES.get('PING'):
                client_socket.sendall(encode_message(MESSAGES.get('PONG')))
