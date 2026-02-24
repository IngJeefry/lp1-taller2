"""
Problema 9: Sistema Distribuido - Backend
✅ Se registra en balanceador
✅ Envía heartbeats
✅ Procesa clientes
✅ Sincroniza datos
"""

import socket
import threading
import time
import sys

class Backend:
    def __init__(self, balancer_host='localhost', balancer_port=8888, my_port=None):
        self.balancer_host = balancer_host
        self.balancer_port = balancer_port
        self.my_port = my_port or self.find_free_port()
        self.server_socket = None
        self.running = False
        
        # Datos locales
        self.data_store = {}
        self.lock = threading.Lock()
        
    def find_free_port(self):
        """Encuentra un puerto libre entre 9001-9099"""
        import random
        return random.randint(9001, 9099)
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.my_port))
        self.server_socket.listen(10)
        self.running = True
        
        print(f"\n🔧 BACKEND iniciado en puerto {self.my_port}")
        
        # ✅ REGISTRO: Registrar en balanceador
        if self.register():
            print(f"✅ Registrado en balanceador {self.balancer_host}:{self.balancer_port}")
        else:
            print(f"❌ No se pudo registrar")
        
        # ✅ HEALTH CHECK: Hilo de heartbeats
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        
        try:
            while self.running:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, 
                               args=(client_sock, addr), daemon=True).start()
        except:
            pass
        finally:
            self.stop()
    
    def register(self):
        """✅ REGISTRO: Enviar registro al balanceador"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.balancer_host, self.balancer_port))
            sock.send(f"REGISTER {self.my_port}\n".encode())
            
            response = sock.recv(1024).decode().strip()
            sock.close()
            return response == "REGISTERED"
        except:
            return False
    
    def heartbeat_loop(self):
        """✅ HEALTH CHECK: Enviar heartbeats cada 3 segundos"""
        while self.running:
            time.sleep(3)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.balancer_host, self.balancer_port))
                sock.send(f"HEARTBEAT {self.my_port}\n".encode())
                sock.recv(1024)  # Recibir respuesta
                sock.close()
                print(f"💓 Heartbeat {self.my_port} OK")
            except:
                print(f"⚠️ Heartbeat {self.my_port} falló")
    
    def handle_client(self, sock, addr):
        """Maneja peticiones de clientes"""
        try:
            data = sock.recv(1024).decode().strip()
            if not data:
                return
            
            print(f"📨 Petición en {self.my_port}: {data}")
            
            parts = data.split()
            cmd = parts[0].upper()
            
            if cmd == "GET" and len(parts) > 1:
                key = parts[1]
                with self.lock:
                    value = self.data_store.get(key, "None")
                response = f"{key}={value}\n"
                
            elif cmd == "SET" and len(parts) > 2:
                key = parts[1]
                value = ' '.join(parts[2:])
                
                with self.lock:
                    self.data_store[key] = value
                
                response = f"OK {key}={value}\n"
                
                # ✅ SINCRONIZACIÓN: Notificar al balanceador
                self.sync_to_balancer(key, value)
                
            elif cmd == "SYNC" and len(parts) > 2:
                # ✅ SINCRONIZACIÓN: Recibir datos de otros backends
                key = parts[1]
                value = ' '.join(parts[2:])
                with self.lock:
                    self.data_store[key] = value
                response = f"SYNCED {key}\n"
                print(f"🔄 Datos sincronizados: {key}={value}")
                
            else:
                response = "ERROR Comando no reconocido\n"
            
            sock.send(response.encode())
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            sock.close()
    
    def sync_to_balancer(self, key, value):
        """✅ SINCRONIZACIÓN: Enviar datos al balanceador"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.balancer_host, self.balancer_port))
            sock.send(f"SYNC {key} {value}\n".encode())
            sock.recv(1024)
            sock.close()
        except:
            pass
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print(f"Backend {self.my_port} cerrado")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    Backend(my_port=port).start()