"""
Problema 9: Sistema Distribuido - Balanceador de Carga
Registro de servidores backend
Health checks
Distribución de clientes (round-robin)
Sincronización de datos
"""

import socket
import threading
import time
import json

class LoadBalancer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        #  REGISTRO: Almacena servidores backend
        self.backends = {}          # (host,port) -> {last_heartbeat, status, data}
        self.backend_list = []       # Lista para round-robin
        self.next_backend = 0
        
        #  SINCRONIZACIÓN: Datos compartidos
        self.data_store = {}         # clave -> valor
        
        self.lock = threading.Lock()
        
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(50)
        self.running = True
        
        print("="*50)
        print(" BALANCEADOR DE CARGA")
        print("="*50)
        print(f"Escuchando en {self.host}:{self.port}\n")
        
        #  HEALTH CHECK: Hilo que monitorea backends
        threading.Thread(target=self.health_check_loop, daemon=True).start()
        
        try:
            while self.running:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, 
                               args=(client_sock, addr), daemon=True).start()
        except:
            pass
        finally:
            self.stop()
    
    def handle_connection(self, sock, addr):
        """Maneja conexiones (backends o clientes)"""
        try:
            data = sock.recv(1024).decode().strip()
            if not data:
                return
            
            parts = data.split()
            cmd = parts[0].upper()
            
            if cmd == "REGISTER":
                #  REGISTRO: Backend se registra
                backend_port = int(parts[1])
                backend_addr = (addr[0], backend_port)
                
                with self.lock:
                    self.backends[backend_addr] = {
                        'last_heartbeat': time.time(),
                        'status': 'healthy',
                        'data': {}  # Datos específicos de este backend
                    }
                    if backend_addr not in self.backend_list:
                        self.backend_list.append(backend_addr)
                    
                    # Enviar datos actuales al nuevo backend
                    for key, value in self.data_store.items():
                        sock.send(f"SYNC {key} {value}\n".encode())
                        time.sleep(0.01)  # Pequeña pausa
                
                sock.send(b"REGISTERED\n")
                print(f" Backend registrado: {backend_addr}")
                
            elif cmd == "HEARTBEAT":
                #  HEALTH CHECK: Backend envía latido
                with self.lock:
                    for backend_addr in self.backends:
                        if backend_addr[1] == int(parts[1]):
                            self.backends[backend_addr]['last_heartbeat'] = time.time()
                            self.backends[backend_addr]['status'] = 'healthy'
                            break
                sock.send(b"HEARTBEAT_OK\n")
                
            elif cmd == "SYNC":
                #  SINCRONIZACIÓN: Backend envía datos actualizados
                if len(parts) >= 3:
                    key = parts[1]
                    value = ' '.join(parts[2:])
                    with self.lock:
                        self.data_store[key] = value
                        # Replicar a otros backends
                        self.replicate_to_all(key, value, exclude=addr)
                    print(f" Datos sincronizados: {key}={value}")
                sock.send(b"SYNCED\n")
                
            elif cmd in ["GET", "SET"]:
                #  DISTRIBUCIÓN: Cliente - redirigir a backend
                self.handle_client_request(sock, data)
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            sock.close()
    
    def handle_client_request(self, sock, request):
        """ DISTRIBUCIÓN: Envía cliente a backend (round-robin)"""
        # Elegir backend saludable
        with self.lock:
            healthy = [b for b in self.backend_list 
                      if b in self.backends and self.backends[b]['status'] == 'healthy']
            
            if not healthy:
                sock.send(b"ERROR No backends disponibles\n")
                return
            
            # Round-robin
            if self.next_backend >= len(healthy):
                self.next_backend = 0
            backend = healthy[self.next_backend]
            self.next_backend += 1
        
        try:
            # Conectar al backend
            backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend_sock.connect(backend)
            backend_sock.send(request.encode())
            
            # Recibir respuesta
            response = backend_sock.recv(4096)
            sock.send(response)
            
        except Exception as e:
            sock.send(f"ERROR Backend no disponible: {e}\n".encode())
            # Marcar como no saludable
            with self.lock:
                if backend in self.backends:
                    self.backends[backend]['status'] = 'unhealthy'
        finally:
            backend_sock.close()
    
    def replicate_to_all(self, key, value, exclude=None):
        """ SINCRONIZACIÓN: Replica datos a todos los backends"""
        for backend_addr in self.backend_list:
            if backend_addr != exclude:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(backend_addr)
                    sock.send(f"SYNC {key} {value}\n".encode())
                    sock.close()
                except:
                    pass
    
    def health_check_loop(self):
        """ HEALTH CHECK: Monitorea backends cada 5 segundos"""
        while self.running:
            time.sleep(5)
            with self.lock:
                now = time.time()
                for backend_addr, info in list(self.backends.items()):
                    # Si no hay heartbeat en 10 segundos, marcar no saludable
                    if now - info['last_heartbeat'] > 10:
                        if info['status'] == 'healthy':
                            info['status'] = 'unhealthy'
                            print(f" Backend {backend_addr} no responde")
                    # Si estaba no saludable y vuelve a responder
                    elif info['status'] == 'unhealthy':
                        info['status'] = 'healthy'
                        print(f" Backend {backend_addr} recuperado")
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("\nBalanceador cerrado")

if __name__ == "__main__":
    LoadBalancer().start()