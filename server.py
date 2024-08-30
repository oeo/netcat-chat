import socket
import threading
import random
import time
import logging
import os
import select
import re

# ANSI color codes
GRAY = "\033[90m"
WHITE = "\033[97m"
PINK = "\033[95m"
RESET = "\033[0m"
ERASE_LINE = "\033[2K"
CURSOR_UP = "\033[1A"

logging.basicConfig(filename='chat_log.txt', level=logging.INFO, format='%(message)s')

def generate_handle():
    return f"user{random.randint(10000, 99999)}"

def format_message(message, color=WHITE):
    current_time = time.strftime("[%H:%M]")
    return f"{color}{current_time} {message}{RESET}"

class Client:
    def __init__(self, socket, handle):
        self.socket = socket
        self.handle = handle

clients = []
clients_lock = threading.Lock()

def is_valid_nick(nick):
    return re.match(r'^[a-zA-Z][a-zA-Z0-9]{0,15}$', nick) is not None

def is_nick_taken(nick):
    with clients_lock:
        return any(client.handle.lower() == nick.lower() for client in clients)

def handle_client(client_socket, addr):
    handle = generate_handle()
    client = Client(client_socket, handle)
    with clients_lock:
        clients.append(client)
        user_count = len(clients)

    # Send initial messages
    help_reminder = f"{GRAY}/? for help{RESET}"
    user_count_message = f"{GRAY}users online: {user_count}{RESET}"
    welcome_message = format_message(f"{handle} connected", GRAY)

    client_socket.sendall(help_reminder.encode() + b"\n")
    client_socket.sendall(user_count_message.encode() + b"\n")
    client_socket.sendall(welcome_message.encode() + b"\n")

    # Broadcast the welcome message to other clients
    broadcast(welcome_message, client)

    # Log and print to server terminal
    logging.info(welcome_message)
    print(welcome_message.lower().rstrip('.'))

    help_message = f"{GRAY}/nick <name> - change your nick\n/list - show online users\n/? - show help \n/bye - disconnect from chat{RESET}"

    try:
        while True:
            ready = select.select([client_socket], [], [], 1)
            if ready[0]:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break

                # Erase the user's input
                client_socket.sendall(f"{CURSOR_UP}{ERASE_LINE}".encode())

                if message.startswith("/nick"):
                    parts = message.split(maxsplit=1)
                    if len(parts) == 1:
                        client_socket.sendall(f"your current nick is: {client.handle}\n".encode())
                    else:
                        new_handle = parts[1]
                        if not is_valid_nick(new_handle):
                            client_socket.sendall(b"invalid nick. must be 1-16 characters, start with a letter, and contain only letters and numbers\n")
                        elif is_nick_taken(new_handle):
                            client_socket.sendall(b"that nick is already taken\n")
                        else:
                            change_message = format_message(f"{client.handle} changed his nick to {new_handle}", GRAY)
                            broadcast(change_message, client)
                            client.handle = new_handle
                            logging.info(change_message)
                            print(change_message.lower().rstrip('.'))  # Print to server terminal
                            client_socket.sendall(change_message.encode() + b"\n")
                elif message == "/list":
                    with clients_lock:
                        user_count = len(clients)
                        online_users = sorted([f"{PINK}{c.handle}{RESET}" if c == client else c.handle for c in clients])
                    user_count_message = f"users online: {user_count}"
                    user_list = "\n".join(online_users)
                    client_socket.sendall(user_count_message.encode() + b"\n")
                    client_socket.sendall(user_list.encode() + b"\n")
                elif message == "/?":
                    client_socket.sendall(help_message.encode() + b"\n")
                elif message == "/bye":
                    goodbye_message = format_message(f"{client.handle} disconnected", GRAY)
                    broadcast(goodbye_message, client)
                    logging.info(goodbye_message)
                    print(goodbye_message.lower().rstrip('.'))  # Print to server terminal
                    client_socket.sendall(f"{GRAY}l8{RESET}\n".encode())
                    break
                else:
                    formatted_message = format_message(f"{PINK}{client.handle}{RESET}: {message}")
                    broadcast(formatted_message, client)
                    logging.info(formatted_message)
                    print(formatted_message.lower().rstrip('.'))  # Print to server terminal
                    client_socket.sendall(formatted_message.encode() + b"\n")
            else:
                # Check if the client is still connected
                try:
                    client_socket.sendall(b'')
                except:
                    break
    except Exception as e:
        logging.error(f"error handling client {client.handle}: {str(e)}")
    finally:
        with clients_lock:
            if client in clients:
                clients.remove(client)
        left_message = format_message(f"{client.handle} disconnected", GRAY)
        broadcast(left_message, client)
        logging.info(left_message)
        print(left_message.lower().rstrip('.'))  # Print to server terminal
        client_socket.close()

def broadcast(message, sender):
    disconnected_clients = []
    with clients_lock:
        for client in clients:
            if client != sender:
                try:
                    client.socket.sendall(message.encode() + b"\n")
                except Exception as e:
                    disconnected_clients.append(client)
                    logging.error(f"error broadcasting to client: {str(e)}")

        for client in disconnected_clients:
            clients.remove(client)
            client.socket.close()

def start_server():
    port = int(os.getenv('CHAT_PORT', 2222))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)

    print(f"server running on :{port}")
    logging.info("chat server started")

    while True:
        client_socket, addr = server.accept()
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
