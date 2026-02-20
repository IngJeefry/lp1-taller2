"""
Problema 5: Transferencia de Archivos - Cliente
Cliente para subir y descargar archivos del servidor
"""

import socket
import os
import hashlib
import sys

class FileClient:
    def __init__(self, host='localhost', port=9999, download_dir='downloads'):
        self.host = host
        self.port = port
        self.download_dir = download_dir
        self.socket = None
        
# Crear directorio de descargas si no existe
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
    
    def connect(self):
        """Conecta al servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Conectado a {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def disconnect(self):
        """Desconecta del servidor"""
        if self.socket:
            self.socket.send("EXIT".encode())
            self.socket.close()
            print("Desconectado del servidor")
    
    def calculate_checksum(self, filepath):
        """Calcula MD5 checksum de un archivo"""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def upload_file(self, filepath):
        """Sube un archivo al servidor"""
        if not os.path.exists(filepath):
            print(f"El archivo {filepath} no existe")
            return
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        checksum = self.calculate_checksum(filepath)
        
        print(f"Subiendo {filename} ({filesize} bytes)...")
        
        try:
# Enviar comando UPLOAD
            self.socket.send(f"UPLOAD {filename} {filesize} {checksum}".encode())
            
# Recibir confirmación
            response = self.socket.recv(1024).decode()
            if not response.startswith("OK"):
                print(f"{response}")
                return
            
            print(f"Servidor listo, enviando archivo...")
            
# Enviar archivo en chunks
            with open(filepath, 'rb') as f:
                sent = 0
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    self.socket.send(chunk)
                    sent += len(chunk)
                    
# Mostrar progreso
                    progress = (sent / filesize) * 100
                    print(f"Progreso: {progress:.1f}%", end='\r')
            
            print()  # Nueva línea
            
# Recibir confirmación final
            final_response = self.socket.recv(1024).decode()
            print(f"{final_response}")
            
        except Exception as e:
            print(f"Error en upload: {e}")
    
    def download_file(self, filename):
        """Descarga un archivo del servidor"""
        print(f"Descargando {filename}...")
        
        try:
# Enviar comando DOWNLOAD
            self.socket.send(f"DOWNLOAD {filename}".encode())
            
# Recibir metadata
            response = self.socket.recv(1024).decode()
            if response.startswith("ERROR"):
                print(f"{response}")
                return
            
# Parsear respuesta DATA
            parts = response.split()
            if parts[0] != "DATA":
                print(f"Respuesta inesperada: {response}")
                return
            
            filesize = int(parts[1])
            expected_checksum = parts[2]
            
            print(f"Servidor listo, descargando {filesize} bytes...")
            
# Confirmar que estamos listos
            self.socket.send("OK".encode())
            
# Recibir archivo en chunks
            filepath = os.path.join(self.download_dir, filename)
            received_data = b''
            remaining = filesize
            
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = self.socket.recv(chunk_size)
                if not chunk:
                    break
                received_data += chunk
                remaining -= len(chunk)
                
# Mostrar progreso
                progress = ((filesize - remaining) / filesize) * 100
                print(f"Progreso: {progress:.1f}%", end='\r')
            
            print()  # Nueva línea
            
# Verificar checksum
            actual_checksum = hashlib.md5(received_data).hexdigest()
            
            if actual_checksum == expected_checksum:
# Guardar archivo
                with open(filepath, 'wb') as f:
                    f.write(received_data)
                print(f"Archivo {filename} descargado correctamente")
                print(f"Guardado en: {filepath}")
            else:
                print(f"Checksum no coincide")
                print(f"   Esperado: {expected_checksum}")
                print(f"   Obtenido: {actual_checksum}")
            
        except Exception as e:
            print(f"Error en download: {e}")
    
    def list_files(self):
        """Lista archivos disponibles en el servidor"""
        print("Solicitando lista de archivos...")
        
        try:
            self.socket.send("LIST".encode())
            response = self.socket.recv(4096).decode()
            
            if response.startswith("OK"):
                files = response[3:].strip()
                if not files:
                    print("No hay archivos en el servidor")
                else:
                    print("\nArchivos disponibles:")
                    print("-" * 40)
                    print(files)
                    print("-" * 40)
            else:
                print(f"{response}")
                
        except Exception as e:
            print(f"Error al listar archivos: {e}")
    
    def run_interactive(self):
        """Modo interactivo del cliente"""
        if not self.connect():
            return
        
        print("\n" + "="*50)
        print("CLIENTE DE TRANSFERENCIA DE ARCHIVOS")
        print("="*50)
        print("Comandos disponibles:")
        print("  upload <archivo>   - Subir archivo al servidor")
        print("  download <archivo> - Descargar archivo del servidor")
        print("  list               - Listar archivos en el servidor")
        print("  exit               - Salir")
        print("="*50 + "\n")
        
        try:
            while True:
                command = input("> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "upload" and len(command) > 1:
                    self.upload_file(command[1])
                elif cmd == "download" and len(command) > 1:
                    self.download_file(command[1])
                elif cmd == "list":
                    self.list_files()
                elif cmd == "exit":
                    break
                else:
                    print("Comando no reconocido")
                    
        except KeyboardInterrupt:
            print("\nSaliendo...")
        finally:
            self.disconnect()

if __name__ == "__main__":
    client = FileClient()
    client.run_interactive()