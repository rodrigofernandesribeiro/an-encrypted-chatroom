# encrypted-chat

a secure end-to-end encrypted chat application with cli interface.

![](https://github.com/0sum-git/an-encrypted-chatroom/blob/main/showcase.gif)

## features

- end-to-end encryption - fernet
- real-time messaging
- message history
- multiple client support
- server dashboard

## installation

```bash
git clone https://github.com/rodrigofernandesribeiro/an-encrypted-chatroom.git
cd encrypted-chat
pip install -r requirements.txt
```

## usage

### start the server

```bash
python chat.py
```

### user

```bash
python chat.py <server_ip>
```

## commands

- `/leave` - exit the chat
- `/shutdown` - shutdown the server (server only)

## requirements

- python 3.8+
- cryptography==41.0.7
