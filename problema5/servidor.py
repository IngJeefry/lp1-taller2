"""
Problema 5: Transferencia de Archivos - Servidor
Implementa un servidor que maneje subida y descarga de archivos
"""

import socket
import threading
import os
import hashlib
import struct

class FileServer:
    def __init__(self, host = 'localhost', port = 9999, storage_dir = 'server_files'):
        self.host = host
        self.port = port
        self.storage_dir = storage_dir
        self.clients = []
        
# Crear directorio de almacenamiento si no existe
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            print(f"Directorio creado: {storage_dir}")
    
    def calculate_checksum(self, data):
        """Calcula MD5 checksum de los datos"""
        return hashlib.md5(data).hexdigest()
    
    def handle_client(self, client_socket, address):
        """Maneja la comunicación con un cliente"""
        print(f"Cliente conectado: {address}")
        
        try:
            while True:
# Recibir comando del cliente
                command_data = client_socket.recv(1024).decode().strip()
                if not command_data:
                    break
                
                print(f"Comando recibido: {command_data}")
                
# Parsear comando
                parts = command_data.split()
                command = parts[0].upper()
                
                if command == "UPLOAD":
                    self.handle_upload(client_socket, parts)
                elif command == "DOWNLOAD":
                    self.handle_download(client_socket, parts)
                elif command == "LIST":
                    self.handle_list(client_socket)
                elif command == "EXIT":
                    break
                else:
                    client_socket.send("ERROR Comando no reconocido".encode())
        
        except Exception as e:
            print(f"Error con cliente {address}: {e}")
        finally:
            client_socket.close()
            print(f"Cliente {address} desconectado")
    
    def handle_upload(self, client_socket, parts):
        """Maneja la subida de archivos"""
        if len(parts) != 4:
            client_socket.send("ERROR Formato: UPLOAD <nombre> <tamaño> <checksum>".encode())
            return
        
        filename = parts[1]
        filesize = int(parts[2])
        expected_checksum = parts[3]
        
# Validar nombre de archivo (seguridad)
        if '..' in filename or '/' in filename:
            client_socket.send("ERROR Nombre de archivo inválido".encode())
            return
        
        filepath = os.path.join(self.storage_dir, filename)
        
        try:
            client_socket.send(f"OK Listo para recibir {filesize} bytes".encode())
            
# Recibir el archivo en chunks
            received_data = b''
            remaining = filesize
            
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = client_socket.recv(chunk_size)
                if not chunk:
                    break
                received_data += chunk
                remaining -= len(chunk)
                
# Mostrar progreso
                progress = ((filesize - remaining) / filesize) * 100
                print(f"Subiendo {filename}: {progress:.1f}%", end='\r')
            
            print()  # Nueva línea después del progreso
            
# Verificar checksum
            actual_checksum = self.calculate_checksum(received_data)
            
            if actual_checksum == expected_checksum:
# Guardar archivo
                with open(filepath, 'wb') as f:
                    f.write(received_data)
                
                client_socket.send(f"OK Archivo {filename} subido correctamente".encode())
                print(f"Archivo {filename} subido ({filesize} bytes)")
            else:
                client_socket.send(f"ERROR Checksum no coincide. Esperado: {expected_checksum}, Obtenido: {actual_checksum}".encode())
                print(f"Checksum incorrecto para {filename}")
                
        except Exception as e:
            client_socket.send(f"ERROR Error en upload: {str(e)}".encode())
            print(f"Error en upload: {e}")
    
    def handle_download(self, client_socket, parts):
        """Maneja la descarga de archivos"""
        if len(parts) != 2:
            client_socket.send("ERROR Formato: DOWNLOAD <nombre>".encode())
            return
        
        filename = parts[1]
        
# Validar nombre de archivo
        if '..' in filename or '/' in filename:
            client_socket.send("ERROR Nombre de archivo inválido".encode())
            return
        
        filepath = os.path.join(self.storage_dir, filename)
        
        if not os.path.exists(filepath):
            client_socket.send("ERROR Archivo no existe".encode())
            return
        
        try:
            filesize = os.path.getsize(filepath)
            
# Leer archivo
            with open(filepath, 'rb') as f:
                file_data = f.read()
            
# Calcular checksum
            checksum = self.calculate_checksum(file_data)
            
# Enviar metadata
            client_socket.send(f"DATA {filesize} {checksum}".encode())
            
# Esperar confirmación
            response = client_socket.recv(1024).decode()
            if response != "OK":
                return
            
# Enviar archivo en chunks
            sent = 0
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    sent += len(chunk)
                    
# Mostrar progreso
                    progress = (sent / filesize) * 100
                    print(f"Enviando {filename}: {progress:.1f}%", end='\r')
            
            print()  # Nueva línea después del progreso
            print(f"Archivo {filename} enviado")
            
        except Exception as e:
            client_socket.send(f"ERROR Error en download: {str(e)}".encode())
            print(f"Error en download: {e}")
    
    def handle_list(self, client_socket):
        """Lista los archivos disponibles"""
        try:
            files = os.listdir(self.storage_dir)
            
            if not files:
                client_socket.send("OK No hay archivos".encode())
                return
            
# Enviar lista de archivos con sus tamaños
            file_list = []
            for f in files:
                filepath = os.path.join(self.storage_dir, f)
                size = os.path.getsize(filepath)
                file_list.append(f"{f} ({size} bytes)")
            
            response = "OK\n" + "\n".join(file_list)
            client_socket.send(response.encode())
            
        except Exception as e:
            client_socket.send(f"ERROR {str(e)}".encode())
    
    def start(self):
        """Inicia el servidor"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"Servidor de archivos iniciado en {self.host}:{self.port}")
        print(f"Almacenando archivos en: {os.path.abspath(self.storage_dir)}")
        print("Esperando conexiones...\n")
        
        try:
            while True:
                client, address = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client, address))
                thread.daemon = True
                thread.start()
                
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario")
        finally:
            server.close()

if __name__ == "__main__":
    server = FileServer()
    server.start()