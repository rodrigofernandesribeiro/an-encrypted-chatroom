import socket
import threading
import sys
import time
import json
import base64
import os
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ChatMessage:
    """classe de uma mensagem de chat e metadados da mesma"""
    def __init__(self, sender, content, msg_type="message", timestamp=None):
        self.timestamp = timestamp if timestamp else datetime.now().strftime("%H:%M:%S")
        self.sender = sender
        self.content = content
        self.msg_type = msg_type
        
    def to_json(self):
        try:
            return json.dumps({
                "timestamp": self.timestamp,
                "sender": self.sender,
                "content": self.content,
                "msg_type": self.msg_type
            })
        except Exception as e:
            raise
    
    @staticmethod
    def from_json(json_str):
        try:
            data = json.loads(json_str)
            return ChatMessage(
                data["sender"], 
                data["content"], 
                data["msg_type"],
                data["timestamp"]
            )
        except json.JSONDecodeError as e:
            raise
        except KeyError as e:
            raise
        except Exception as e:
            raise

class Encryption:
    """classe para gerir a criptografia de mensagens"""
    def __init__(self):
        try:
            self.key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.key)
        except Exception as e:
            raise
    
    def encrypt(self, message):
        try:
            if not isinstance(message, str):
                message = str(message)
            message_bytes = message.encode('utf-8')
            encrypted_data = self.cipher_suite.encrypt(message_bytes)
            return base64.b64encode(encrypted_data)
        except Exception as e:
            raise
    
    def decrypt(self, encrypted_message):
        try:
            if not isinstance(encrypted_message, bytes):
                encrypted_message = bytes(encrypted_message)
            encrypted_data = base64.b64decode(encrypted_message)
            return self.cipher_suite.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            raise

class ChatUI:
    """classe para gerir a interface do utilizador do chat"""
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header():
        ChatUI.clear_screen()
        print("=" * 60)
        print("                   servidor de chat encriptado")
        print("=" * 60)
        print()
    
    @staticmethod
    def print_message(message):
        if message.msg_type == "system":
            print(f"[{message.timestamp}] sistema: {message.content}")
        elif message.sender == "server":
            print(f"[{message.timestamp}] servidor: {message.content}")
        else:
            print(f"[{message.timestamp}] {message.sender}: {message.content}")
    
    @staticmethod
    def print_error(message):
        print(f"erro: {message}")
    
    @staticmethod
    def print_info(message):
        print(f"info: {message}")
    
    @staticmethod
    def print_prompt():
        print("> ", end="", flush=True)
    
    @staticmethod
    def print_welcome(username):
        ChatUI.clear_screen()
        ChatUI.print_header()
        print(f"olá, {username}! estás conectado ao chat.")
        print(f"escreve '/leave' para sair do chat.")
        print()
        print("-" * 60)
        print()
    
    @staticmethod
    def print_users_table(users):
        if not users:
            print("nenhum utilizador conectado\n")
            return
            
        # obtém a lista de nomes de utilizadores
        usernames = list(users)
        
        # calcula larguras das colunas
        username_width = max(len("utilizador"), max(len(username) for username in usernames))
        id_width = max(len("id"), len(str(len(usernames))))
        
        # imprime cabeçalho
        print("+"+"-" * (username_width + id_width + 5)+"+")
        print(f"| {'utilizador':<{username_width}} | {'id':<{id_width}} |")
        print("+"+"-" * (username_width + id_width + 5)+"+")
        
        # imprime utilizadores
        for i, username in enumerate(usernames, 1):
            print(f"| {username:<{username_width}} | {i:<{id_width}} |")
        print("+" + "-" * (username_width + id_width + 5) + "+")
        print()
    
    @staticmethod
    def print_server_dashboard(server):
        ChatUI.clear_screen()
        ChatUI.print_header()
        
        print("informações do servidor")
        print("-" * 60)
        print(f"estado: em execução")
        print(f"porta: {server.port}")
        print(f"tempo de atividade: {server.get_uptime()}")
        print(f"total de mensagens: {len(server.message_history)}")
        print(f"utilizadores conectados: {len(server.clients)}")
        print()
        
        print("utilizadores conectados")
        print("-" * 60)
        ChatUI.print_users_table(list(server.clients.keys()))
        
        print("mensagens recentes")
        print("-" * 60)
        recent_messages = server.message_history[-5:] if server.message_history else []
        if recent_messages:
            for msg in recent_messages:
                ChatUI.print_message(msg)
        else:
            print("ainda não há mensagens")
        print()
        
        print("mensagens de informação")
        print("-" * 60)
        if server.info_messages:
            for msg in server.info_messages:
                print(msg)
        else:
            print("ainda não há mensagens de informação")
        print()
        
        print("comandos disponíveis")
        print("-" * 60)
        print("/shutdown - para o servidor")
        print()
        
        ChatUI.print_prompt()

class Server:
    """servidor de chat que gere conexões e mensagens"""
    def __init__(self, port=10000):
        self.port = port
        self.server_socket = None
        self.clients = {}  
        self.connections = set() 
        self.message_history = []
        self.info_messages = []
        self.running = False
        self.start_time = None
        self.encryption = Encryption()
        self.lock = threading.Lock()  # lock para sincronização
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(5)
            self.running = True
            self.start_time = time.time()
            
            # inicia thread para atualização do dashboard
            self.dashboard_thread = threading.Thread(target=self.update_dashboard_loop)
            self.dashboard_thread.daemon = True
            self.dashboard_thread.start()
        except Exception as e:
            raise
    
    def update_dashboard_loop(self):
        """atualiza o dashboard periodicamente"""
        while self.running:
            try:
                with self.lock:
                    self.update_dashboard()
                time.sleep(5)  # atualiza a cada 5 segundos
            except Exception as e:
                time.sleep(5)  # espera antes de tentar novamente
    
    def add_info_message(self, message):
        with self.lock:
            self.info_messages.append(message)
            if len(self.info_messages) > 5:
                self.info_messages.pop(0)
    
    def get_uptime(self):
        if not self.start_time:
            return "0:00:00"
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def update_dashboard(self):
        try:
            ChatUI.print_server_dashboard(self)
        except Exception as e:
            raise
    
    def accept_connections(self):
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                with self.lock:
                    self.connections.add(client_socket)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    raise
    
    def handle_client(self, client_socket, address):
        username = None
        
        try:
            client_socket.sendall(self.encryption.key)
            
            username_data = client_socket.recv(1024)
            if not username_data:
                return
            
            username = self.encryption.decrypt(username_data)
            with self.lock:
                self.clients[username] = client_socket
            self.send_message_history(client_socket)
            
            welcome_msg = ChatMessage("sistema", f"{username} entrou no chat", "system")
            self.broadcast_message(welcome_msg)
            
            while self.running:
                encrypted_data = client_socket.recv(1024)
                if not encrypted_data:
                    break
                
                message_data = self.encryption.decrypt(encrypted_data)
                message = ChatMessage.from_json(message_data)
                
                if message.content == "/leave":
                    break
                
                self.broadcast_message(message)
                
        except Exception as e:
            raise
        finally:
            if username:
                self.remove_client(client_socket)
    
    def remove_client(self, client_socket):
        username = None
        with self.lock:
            for name, socket in self.clients.items():
                if socket == client_socket:
                    username = name
                    break
            
            if username:
                self.clients.pop(username, None)
                self.connections.discard(client_socket)
                
                goodbye_msg = ChatMessage("sistema", f"{username} saiu do chat", "system")
                self.broadcast_message(goodbye_msg)
                
                try:
                    client_socket.close()
                except:
                    pass
    
    def send_message_history(self, client_socket):
        try:
            with self.lock:
                for message in self.message_history:
                    self.send_to_client(client_socket, message)
        except Exception as e:
            raise
    
    def send_to_client(self, client_socket, message):
        try:
            json_data = message.to_json()
            encrypted_data = self.encryption.encrypt(json_data)
            client_socket.sendall(encrypted_data)
        except Exception as e:
            raise
    
    def broadcast_message(self, message):
        with self.lock:
            self.message_history.append(message)
            if len(self.message_history) > 100:
                self.message_history.pop(0)
            
            connections_copy = self.connections.copy()
            for client_socket in connections_copy:
                try:
                    self.send_to_client(client_socket, message)
                except:
                    self.remove_client(client_socket)
    
    def server_input(self):
        while self.running:
            try:
                command = input().strip()
                if command == "/shutdown":
                    self.running = False
                    break
            except Exception as e:
                raise

class Client:
    """cliente de chat que se conecta ao servidor"""
    def __init__(self, host, port=10000):
        self.host = host
        self.port = port
        self.socket = None
        self.encryption = None
        self.username = None
        self.running = False
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            raise
    
    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            
            key = self.socket.recv(1024)
            self.encryption = Encryption()
            self.encryption.key = key
            self.encryption.cipher_suite = Fernet(key)
            
            self.username = input("nome de utilizador: ").strip()
            encrypted_username = self.encryption.encrypt(self.username)
            self.socket.sendall(encrypted_username)
            
            self.running = True
            return True
        except Exception as e:
            raise
    
    def disconnect(self):
        try:
            self.running = False
            if self.socket:
                self.socket.close()
        except Exception as e:
            raise
    
    def receive_messages(self):
        while self.running:
            try:
                encrypted_data = self.socket.recv(1024)
                if not encrypted_data:
                    break
                
                message_data = self.encryption.decrypt(encrypted_data)
                message = ChatMessage.from_json(message_data)
                ChatUI.print_message(message)
            except Exception as e:
                break
    
    def send_messages(self):
        while self.running:
            try:
                message = input().strip()
                if message == "/leave":
                    self.running = False
                    break
                
                chat_message = ChatMessage(self.username, message)
                json_data = chat_message.to_json()
                encrypted_data = self.encryption.encrypt(json_data)
                self.socket.sendall(encrypted_data)
            except Exception as e:
                break

def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
        client = Client(host)
        try:
            if client.connect():
                ChatUI.print_welcome(client.username)
                receive_thread = threading.Thread(target=client.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                client.send_messages()
        except Exception as e:
            ChatUI.print_error(str(e))
        finally:
            client.disconnect()
    else:
        server = Server()
        try:
            # mostra o dashboard inicial
            ChatUI.print_server_dashboard(server)
            # inicia a thread de aceitação de conexões
            accept_thread = threading.Thread(target=server.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            # inicia o loop de entrada do servidor
            server.server_input()
        except Exception as e:
            ChatUI.print_error(str(e))
        finally:
            server.running = False
            if server.server_socket:
                server.server_socket.close()

if __name__ == "__main__":
    main()