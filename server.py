import socket
import threading
from Yuvi import decode_header, decode_message

host = '0.0.0.0'
port = 65432

HEADER_SIZE = 4

'''
protocol
# [magic_number] - number the server sends each client upon connection to verify him
[header] - 4 bytes that represent the length of the message to come
[message] - 'header' length bytes that contains the command
    - command
'''


def ping_handler():
    print("Received ping")
    return True


def default_handler():
    print("Received unknown message")
    return False


message_handlers = {
    'PING': ping_handler
}


def handle_client(connection, address):
    print(f"[handle_client] Starting to handle client {connection} {address}")
    connected = True

    while connected:
        message_length = decode_header(connection.recv(HEADER_SIZE))
        message = decode_message(connection.recv(message_length))
        message_handler = message_handlers.get(message, default_handler)

        connected = message_handler()

    connection.close()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            client_connection, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_connection, client_address))
            thread.start()

            print(f"Received connection")


start_server()
