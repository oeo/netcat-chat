import socket
import threading
import random
import time
import logging

# ANSI color codes
GRAY = "\033[90m"
WHITE = "\033[97m"
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

def handle_client(client_socket, addr):
    handle = generate_handle()
    client = Client(client_socket, handle)
    clients.append(client)
    welcome_message = format_message(f"{handle} has joined", GRAY)
    broadcast(welcome_message, client)
    logging.info(welcome_message)
    print(welcome_message)  # Print to server terminal

    client_socket.send(welcome_message.encode() + b"\n")
    help_message = f"{GRAY}commands:\n/nick <name> - change your nick\n/list - show online users\n/help - show help message\n/bye or /exit - disconnect from chat{RESET}"
    client_socket.send(help_message.encode() + b"\n")

    while True:
        try:
            message = client_socket.recv(1024).decode().strip()
            if message is None:  # Connection closed
                break
            if not message:  # Empty message
                continue

            # Erase the user's input
            client_socket.send(f"{CURSOR_UP}{ERASE_LINE}".encode())

            if message.startswith("/nick "):
                new_handle = message.split(" ", 1)[1]
                change_message = format_message(f"{client.handle} changed his handle to {new_handle}", GRAY)
                broadcast(change_message, client)
                client.handle = new_handle
                logging.info(change_message)
                print(change_message)  # Print to server terminal
                client_socket.send(change_message.encode() + b"\n")
            elif message == "/list":
                online_users = sorted([c.handle for c in clients])
                user_list = f"{GRAY}" + "\n".join(online_users) + f"{RESET}"
                client_socket.send(user_list.encode() + b"\n")
            elif message == "/help":
                client_socket.send(help_message.encode() + b"\n")
            elif message in ["/bye", "/exit"]:
                goodbye_message = format_message(f"{client.handle} has left", GRAY)
                broadcast(goodbye_message, client)
                logging.info(goodbye_message)
                print(goodbye_message)  # Print to server terminal
                client_socket.send(f"{GRAY}l8{RESET}\n".encode())
                break
            else:
                formatted_message = format_message(f"{client.handle}: {message}")
                broadcast(formatted_message, client)
                logging.info(formatted_message)
                print(formatted_message)  # Print to server terminal
                client_socket.send(formatted_message.encode() + b"\n")
        except Exception as e:
            logging.error(f"error handling client {client.handle}: {str(e)}")
            break

    clients.remove(client)
    client_socket.close()

def broadcast(message, sender):
    disconnected_clients = []
    for client in clients:
        if client != sender:
            try:
                client.socket.send(message.encode() + b"\n")
            except Exception as e:
                disconnected_clients.append(client)
                logging.error(f"error broadcasting to client: {str(e)}")

    for client in disconnected_clients:
        clients.remove(client)
        client.socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 2222))
    server.listen(5)

    print("server running on :2222")
    logging.info("chat server started")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

clients = []

if __name__ == "__main__":
    start_server()
