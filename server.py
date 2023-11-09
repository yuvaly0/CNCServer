import socket
import threading

host = '0.0.0.0'
port = 65432

def handle_client(connection, address):
    print(f"[handle_client] Starting to handle client {connection} {address}")
    connected = True
    while connected:
        pass

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
