# chat-encriptado

uma aplicação de chat segura com encriptação ponto-a-ponto cli.

## funcionalidades

- encriptação ponto-a-ponto - fernet
- mensagens em tempo real
- histórico de mensagens
- suporte para múltiplos clientes
- server dashboard

## instalação

```bash
git clone https://github.com/rodrigofernandesribeiro/an-encrypted-chatroom.git
cd chat-encriptado
pip install -r requirements.txt
```

## utilização

### iniciar o servidor

```bash
python chat.py
```

### user

```bash
python chat.py <ip_do_servidor>
```

## comandos

- `/leave` - sair do chat
- `/shutdown` - parar o servidor (apenas servidor)

## requisitos

- python 3.8+
- cryptography==41.0.7
