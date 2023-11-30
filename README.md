# Python CNC Server

## Overview

This CNC Server is a python single-threaded server application designed to handle multiple client connections 
using non-blocking I/O with the `select` method.

## Features

- **Non-blocking Socket I/O**: Leverages `select` for efficient I/O across multiple client connections.
- **Custom Protocol Handling**: Implements a protocol for message encoding and decoding.
- **Periodic Pings**: Sends "PING" messages to connected clients at regular intervals to maintain connection integrity.
- **Timestamp Inclusion**: Each message includes a timestamp, allowing for latency calculations and time tracking.
- **Magic Inclusion**: Each message includes a magic, allowing for filtering messages for verification.
- **Custom Commands**: Able to send command with variable number of commands to the client
- **Connection Management**: Efficiently handles new connections, client disconnections, and data transmission.

## Requirements

- Python 3.x

## Installation

To get started with this server, clone the repository to your local machine:

```bash
git clone https://github.com/yuvaly0/CNCServer.git
cd CNCServer
```

## Usage

Run the server using the following command:

```bash
python server.py
```

## Project Structure

The project is structured into several files, each serving a specific purpose:

- `server.py`: This file is the entry point, it is responsible for initializing the `CNCServer` class and calling `start_server()` on it

- `cnc_server.py`: Contains the `CNCServer` class, which encapsulates the logic for the CNC server. This includes initializing the server socket, handling incoming connections, managing client communication, and periodically sending pings to connected clients.

- `communication.py`: This file contains the utility functions for message encoding, decoding, and timestamp formatting. based on the custom protocol we wrote.

## TODO
- Support cli usage using `sys.stdin`