def encode_message(message):
    header = str(len(message)).rjust(4, '0')
    encoded_msg = bytes(header + message, encoding='utf-8')

    return encoded_msg


def decode_header(encoded_header):
    message_header_received = encoded_header.decode('utf-8')

    if message_header_received == '':
        return -1

    message_length = int(message_header_received)
    return message_length


def decode_message(encoded_message):
    return encoded_message.decode('utf-8')


MESSAGES = {
    'PONG': 'PONG',
    'PING': 'PING'
}
