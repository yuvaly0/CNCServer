import socket
from Yuvi import encode_message

HOST = '127.0.0.1'
PORT = 65432

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def send(msg):
    # todo: try to send the header as bytes
    client.send(encode_message(msg))


send("PING")
