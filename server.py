import socket
import select
from Yuvi import decode_header, decode_message, encode_message

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


def handle_recv_msg(current_socket):
    message_length = decode_header(current_socket.recv(HEADER_SIZE))

    if message_length == -1:
        return False

    message = decode_message(current_socket.recv(message_length))
    print(f'Received {message}')
    return True


def handle_send_msg(current_socket, message_queues):
    try:
        current_msg = message_queues[current_socket]
        current_socket.sendall(encode_message(current_msg))
    except Exception as e:
        pass


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
            readable, writeable, exceptional = select.select(inputs, outputs, [])

            for current_socket in readable:
                if current_socket is server_socket:
                    connection, client_address = current_socket.accept()
                    connection.setblocking(False)
                    inputs.append(current_socket)
                    outputs.append(current_socket)

                    message_queues[connection] = b'ping'
                else:
                    result = handle_recv_msg(current_socket)

                    if not result:
                        current_socket.close()

            for current_socket in writeable:
                try:
                    handle_send_msg(current_socket, message_queues)
                except Exception as e:
                    pass

            for current_socket in exceptional:
                inputs.remove(current_socket)
                if current_socket in outputs:
                    outputs.remove(current_socket)

                current_socket.close()


start_server()
