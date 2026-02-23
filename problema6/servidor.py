"""
Problema 6: Chat con Salas - Servidor
Múltiples salas, mensajes privados y gestión de usuarios
"""

import socket
import threading
import json
import time
from collections import defaultdict

class ChatRoom:
    """Representa una sala de chat"""
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.clients = set()  # Clientes en esta sala
        self.created_at = time.time()
    
    def add_client(self, client):
        self.clients.add(client)
    
    def remove_client(self, client):
        self.clients.discard(client)
    
    def get_users(self):
        """Retorna lista de nombres de usuarios en la sala"""
        return [client.nickname for client in self.clients]
    
    def broadcast(self, message, sender=None, exclude=None):
        """Envía mensaje a todos en la sala excepto exclude"""
        for client in self.clients:
            if client != exclude and client != sender:
                client.send_message(message)

class ChatClient:
    """Representa un cliente conectado"""
    def __init__(self, socket, address, server):
        self.socket = socket
        self.address = address
        self.server = server
        self.nickname = None
        self.current_room = None
        self.buffer = ""
        
    def send_message(self, message):
        """Envía un mensaje al cliente"""
        try:
            self.socket.send(f"{message}\n".encode())
        except:
            self.server.remove_client(self)
    
    def handle_message(self, message):
        """Procesa un mensaje del cliente"""
        if message.startswith('/'):
            self.handle_command(message)
        else:
            # Mensaje normal a la sala actual
            if self.current_room:
                room = self.server.rooms[self.current_room]
                formatted = f"[{self.current_room}] {self.nickname}: {message}"
                room.broadcast(formatted, sender=self)
                print(formatted)
            else:
                self.send_message("No estás en ninguna sala. Usa /JOIN o /CREATE")
    
    def handle_command(self, command):
        """Procesa comandos del cliente"""
        parts = command.strip().split()
        cmd = parts[0].lower()
        
        if cmd == '/create' and len(parts) > 1:
            room_name = parts[1]
            if room_name in self.server.rooms:
                self.send_message(f"La sala '{room_name}' ya existe")
            else:
                self.server.rooms[room_name] = ChatRoom(room_name, self.nickname)
                self.send_message(f"Sala '{room_name}' creada")
                # Auto-unirse a la sala creada
                self.join_room(room_name)
        
        elif cmd == '/join' and len(parts) > 1:
            room_name = parts[1]
            if room_name not in self.server.rooms:
                self.send_message(f"La sala '{room_name}' no existe. Usa /CREATE o /LIST")
            else:
                self.join_room(room_name)
        
        elif cmd == '/leave':
            self.leave_current_room()
        
        elif cmd == '/list':
            self.list_rooms()
        
        elif cmd == '/users':
            if self.current_room:
                room = self.server.rooms[self.current_room]
                users = room.get_users()
                self.send_message(f"Usuarios en '{self.current_room}': {', '.join(users)}")
            else:
                self.send_message("No estás en ninguna sala")
        
        elif cmd == '/msg' and len(parts) > 2:
            target = parts[1]
            private_msg = ' '.join(parts[2:])
            self.send_private_message(target, private_msg)
        
        elif cmd == '/help':
            self.show_help()
        
        elif cmd == '/exit':
            self.server.remove_client(self)
        
        else:
            self.send_message("Comando no reconocido. Usa /HELP para ayuda")
    
    def join_room(self, room_name):
        """Unir a una sala"""
        # Salir de la sala actual si está en una
        self.leave_current_room()
        
        room = self.server.rooms[room_name]
        room.add_client(self)
        self.current_room = room_name
        
        # Notificar a la sala
        welcome = f"{self.nickname} se ha unido a la sala"
        room.broadcast(welcome, exclude=self)
        self.send_message(f"Te has unido a '{room_name}'")
        
        print(f"{self.nickname} se unió a '{room_name}'")
    
    def leave_current_room(self):
        """Salir de la sala actual"""
        if self.current_room and self.current_room in self.server.rooms:
            room = self.server.rooms[self.current_room]
            room.remove_client(self)
            
            # Notificar a la sala
            goodbye = f"{self.nickname} ha abandonado la sala"
            room.broadcast(goodbye, exclude=self)
            
            # Si la sala queda vacía y no es la sala general, se elimina
            if len(room.clients) == 0 and self.current_room != "general":
                del self.server.rooms[self.current_room]
                print(f"Sala '{self.current_room}' eliminada (vacía)")
            
            self.current_room = None
    
    def list_rooms(self):
        """Lista todas las salas disponibles"""
        if not self.server.rooms:
            self.send_message("No hay salas disponibles. Usa /CREATE para crear una")
            return
        
        rooms_info = []
        for name, room in self.server.rooms.items():
            users_count = len(room.clients)
            creator = room.creator if hasattr(room, 'creator') else "desconocido"
            rooms_info.append(f"  • {name} ({users_count} usuarios) - creada por {creator}")
        
        self.send_message("Salas disponibles:\n" + "\n".join(rooms_info))
    
    def send_private_message(self, target_nick, message):
        """Envía un mensaje privado a otro usuario"""
        target_client = self.server.find_client_by_nickname(target_nick)
        
        if target_client:
            formatted = f"[MP de {self.nickname}]: {message}"
            target_client.send_message(formatted)
            self.send_message(f"[MP para {target_nick}]: {message}")
        else:
            self.send_message(f"Usuario '{target_nick}' no encontrado")
    
    def show_help(self):
        """Muestra ayuda de comandos"""
        help_text = """
COMANDOS DISPONIBLES:
  /CREATE <sala>   - Crear nueva sala
  /JOIN <sala>     - Unirse a una sala
  /LEAVE           - Salir de la sala actual
  /LIST            - Listar salas disponibles
  /USERS           - Ver usuarios en la sala actual
  /MSG <usr> <txt> - Enviar mensaje privado
  /HELP            - Mostrar esta ayuda
  /EXIT            - Desconectarse
  
  Sin comando: mensaje público a la sala actual
"""
        self.send_message(help_text)

class ChatServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.clients = {}  # socket -> ChatClient
        self.rooms = {}    # nombre -> ChatRoom
        self.lock = threading.Lock()
        
        # Crear sala general por defecto
        self.rooms['general'] = ChatRoom('general', 'system')
    
    def find_client_by_nickname(self, nickname):
        """Busca un cliente por su nickname"""
        for client in self.clients.values():
            if client.nickname == nickname:
                return client
        return None
    
    def remove_client(self, client):
        """Elimina un cliente desconectado"""
        with self.lock:
            if client.socket in self.clients:
                # Salir de la sala actual
                client.leave_current_room()
                
                # Notificar a todos
                if client.nickname:
                    print(f"Cliente {client.nickname} desconectado")
                
                del self.clients[client.socket]
                client.socket.close()
    
    def handle_client(self, sock, addr):
        """Maneja la comunicación con un cliente"""
        client = ChatClient(sock, addr, self)
        
        try:
            # Solicitar nickname
            client.send_message("Bienvenido al Chat con Salas. ¿Cuál es tu nombre?")
            nickname = sock.recv(1024).decode().strip()
            
            if not nickname:
                return
            
            # Verificar si el nickname ya existe
            with self.lock:
                if self.find_client_by_nickname(nickname):
                    client.send_message("Ese nombre ya está en uso. Desconectando...")
                    return
                
                client.nickname = nickname
                self.clients[sock] = client
            
            print(f"✅ Cliente {nickname} conectado desde {addr}")
            client.send_message(f"Bienvenido {nickname}! Usa /HELP para comandos")
            
            # Unir a sala general por defecto
            client.join_room('general')
            
            # Bucle principal de mensajes
            buffer = ""
            while True:
                data = sock.recv(1024).decode()
                if not data:
                    break
                
                # Manejar múltiples líneas
                buffer += data
                if '\n' in buffer:
                    lines = buffer.split('\n')
                    buffer = lines[-1]
                    
                    for line in lines[:-1]:
                        if line.strip():
                            client.handle_message(line.strip())
        
        except Exception as e:
            print(f"Error con cliente {addr}: {e}")
        finally:
            self.remove_client(client)
    
    def start(self):
        """Inicia el servidor"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"Servidor de Chat con Salas iniciado en {self.host}:{self.port}")
        print(f"Sala por defecto: 'general'")
        print("Esperando conexiones...\n")
        
        try:
            while True:
                client_sock, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_sock, addr))
                thread.daemon = True
                thread.start()
                
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario")
        finally:
            server.close()

if __name__ == "__main__":
    server = ChatServer()
    server.start()