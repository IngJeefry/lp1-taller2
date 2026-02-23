"""
Problema 6: Chat con Salas - Cliente
Cliente con soporte para múltiples salas y mensajes privados
"""

import socket
import threading
import sys
import os
import signal

class ChatClient:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.nickname = None
    
    def connect(self):
        """Conecta al servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def receive_messages(self):
        """Hilo para recibir mensajes del servidor"""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                if '\n' in buffer:
                    lines = buffer.split('\n')
                    buffer = lines[-1]
                    
                    for line in lines[:-1]:
                        # Limpiar línea y mostrar
                        print(f"\r{line}")
                        print("> ", end="", flush=True)
                        
            except:
                break
        
        print("\nConexión perdida con el servidor")
        self.running = False
    
    def send_message(self, message):
        """Envía un mensaje al servidor"""
        try:
            self.socket.send(f"{message}\n".encode())
        except:
            print("Error al enviar mensaje")
            self.running = False
    
    def run(self):
        """Ejecuta el cliente"""
        if not self.connect():
            return
        
        # Solicitar nickname
        response = self.socket.recv(1024).decode().strip()
        print(response)
        nickname = input("> ")
        self.socket.send(f"{nickname}\n".encode())
        self.nickname = nickname
        
        # Recibir respuesta del servidor
        response = self.socket.recv(1024).decode().strip()
        print(response)
        
        # Verificar si fue exitoso
        if "ERROR" in response:
            self.socket.close()
            return
        
        self.running = True
        
        # Iniciar hilo de recepción
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        print("\n" + "="*50)
        print("CHAT CON SALAS - COMANDOS:")
        print("  /CREATE <sala>   - Crear sala")
        print("  /JOIN <sala>     - Unirse a sala")
        print("  /LEAVE           - Salir de sala actual")
        print("  /LIST            - Listar salas")
        print("  /USERS           - Ver usuarios en sala")
        print("  /MSG <usr> <txt> - Mensaje privado")
        print("  /HELP            - Mostrar ayuda")
        print("  /EXIT            - Salir")
        print("="*50 + "\n")
        
        # Bucle principal para enviar mensajes
        try:
            while self.running:
                message = input("> ")
                if message.strip():
                    self.send_message(message)
                    if message == "/exit":
                        break
        except KeyboardInterrupt:
            print("\nSaliendo...")
        finally:
            self.running = False
            self.socket.close()
            print("Desconectado")

class SimpleClient:
    """Versión más simple sin threads para pruebas básicas"""
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.socket = None
    
    def run_simple(self):
        """Versión simple sin threads (send/receive alternados)"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Recibir solicitud de nombre
            print(self.socket.recv(1024).decode().strip())
            nickname = input()
            self.socket.send(f"{nickname}\n".encode())
            
            # Recibir respuesta
            print(self.socket.recv(1024).decode().strip())
            
            # Bucle simple (solo envía, recibe después)
            while True:
                message = input("> ")
                if not message:
                    continue
                    
                self.socket.send(f"{message}\n".encode())
                
                if message == "/exit":
                    break
                
                # Recibir respuesta (puede haber múltiples)
                self.socket.settimeout(0.5)
                try:
                    while True:
                        response = self.socket.recv(1024).decode().strip()
                        if response:
                            print(response)
                except socket.timeout:
                    pass
                finally:
                    self.socket.settimeout(None)
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    # Usar versión con threads por defecto
    client = ChatClient()
    client.run()
    
    # Para versión simple, descomentar:
    # client = SimpleClient()
    # client.run_simple()