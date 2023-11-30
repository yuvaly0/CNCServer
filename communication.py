from datetime import datetime

TIMESTAMP_LENGTH = 26
HEADER_LENGTH_FIELD_SIZE = 4
DELIMITER = '$'
MAGIC = 'AEQP'
HEADER_SIZE = len(MAGIC) + HEADER_LENGTH_FIELD_SIZE

"""
protocol docs

[header] - 4 bytes that represent the length of the message to come
    -   magic - 4 bytes
    -   length - 4 bytes
[message] - 'header' length bytes that contains the command
    - timestamp string, iso format
    - message
"""


def format_timestamp(timestamp):
    truncated_microseconds = int(timestamp.microsecond / 1000) * 1000
    timestamp = timestamp.replace(microsecond=truncated_microseconds)

    return timestamp

def encode_message(command, params):
    timestamp = format_timestamp(datetime.now())
    full_message = f"{timestamp}{command}{DELIMITER}{DELIMITER.join(params)}"

    header = MAGIC + str(len(full_message)).rjust(HEADER_LENGTH_FIELD_SIZE, '0')
    encoded_msg = bytes(header + full_message, encoding='utf-8')

    return encoded_msg


def decode_header(encoded_header):
    message_header_received = encoded_header.decode('utf-8')

    if message_header_received == '':
        return -1

    if not message_header_received.startswith(MAGIC):
        return -1

    message_header = message_header_received[len(MAGIC):]

    message_length = int(message_header)
    return message_length


def decode_message(encoded_message):
    decoded_message = encoded_message.decode('utf-8')

    # Split the message to separate timestamp and actual message
    timestamp_string = decoded_message[:TIMESTAMP_LENGTH]
    raw_message = decoded_message[TIMESTAMP_LENGTH:]

    # Extract command and parameters
    message = raw_message.split(DELIMITER)
    command = message[0]
    parameters = message[1:]

    try:
        timestamp = datetime.fromisoformat(timestamp_string)
        return timestamp, command, parameters
    except ValueError:
        return None, None, []


MESSAGES = {
    'PONG': 'PONG',
    'PING': 'PING',
    'EXEC': 'EXEC'
}

