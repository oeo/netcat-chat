# netcat-chat

this is a simple terminal-based chat server written in python. the server allows multiple users to connect via a tcp socket and chat with each other in real-time. users can change their nickname, see a list of online users, and gracefully exit the chat. all server-side messages (such as user join/leave notifications and nick changes) are logged to a file named `chat_log.txt` and displayed in the server's console.

## features

- **unique handles:** each user is assigned a unique handle when they join the chat, which can be changed using the `/nick` command.
- **color-coded messages:** system messages, such as user join/leave notifications and nick changes, are displayed in gray to differentiate them from user chat messages, which are displayed in white.
- **input management:** the server automatically erases the user's input after they send a message. this keeps the chat output clean.
- **command support:** users can change their nickname, view a list of online users, get a help message, and exit the chat using simple commands.
- **logging:** all chat activity, including messages, nick changes, and join/leave events, is logged to `chat_log.txt` for auditing or review purposes.

## usage

### prerequisites

- python 3.x installed on your machine

### setup and running the server

1. save the provided script as `server.py`.
2. open a terminal and navigate to the directory containing `server.py`.
3. run the following command to start the server:

   ```bash
   python3 server.py
   ```

   the server will start and listen on port `2222` for incoming connections.

### connecting to the chat server

users can connect to the chat server using any tcp client that allows raw tcp connections. `nc` (netcat) is a popular option.

1. open a terminal.
2. use `nc` to connect to the server:

   ```bash
   nc <server_ip_address> 2222
   ```

   replace `<server_ip_address>` with the ip address or hostname of the machine running the chat server.

### commands

- `/nick <name>`: change your nickname to `<name>`.
- `/list`: display a list of online users.
- `/help`: show a list of available commands.
- `/bye` or `/exit`: gracefully exit the chat.

### example session

```bash
$ nc chat.example.com 2222
[07:14] user12345 has joined
commands:
/nick <name> - change your nick
/list - show online users
/help - show help message
/bye or /exit - disconnect from chat
/nick john
[07:15] user12345 changed his handle to john
hello everyone!
[07:15] john: hello everyone!
/list
john
user67890
/bye
[07:16] john has left
```

### logging

chat activity is logged to `chat_log.txt` in the same directory as `server.py`. the log file includes:

- timestamps for each event
- join and leave messages
- nickname changes
- chat messages

### customization

- **port number:** to change the port number, modify the `server.bind(('0.0.0.0', 2222))` line in `server.py` to use the desired port.
- **handle format:** to adjust the format of the unique handles assigned to users, modify the `generate_handle()` function.
- **colors:** colors are handled using ansi escape codes. these can be adjusted by changing the values of `GRAY`, `WHITE`, and `RESET` in the script.

## conclusion

this chat server provides a simple yet functional interface for multiple users to communicate in real-time via a terminal. it supports essential chat functionalities like nicknames, user listings, and connection management. although it has basic features, it is extensible and can be customized to suit more complex use cases.

