"""
Problema 7: Proxy HTTP (Intermediario de red)
- Recibe peticiones del cliente
- Conecta al servidor destino
- Reenvía datos bidireccionalmente
- Soporta HTTP y HTTPS (método CONNECT)
"""

import socket
import threading
import sys
import time
from urllib.parse import urlparse

class HTTPProxy:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.proxy_socket = None
        self.running = False
        self.request_count = 0
        self.byte_count = 0
        
    def start(self):
        """Inicia el servidor proxy"""
        try:
            self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.proxy_socket.bind((self.host, self.port))
            self.proxy_socket.listen(100)  # Cola de hasta 100 conexiones
            self.running = True
            
            print(f"Proxy HTTP iniciado en {self.host}:{self.port}")
            print("Esperando conexiones de clientes...")
            print("   (Presiona Ctrl+C para detener)\n")
            
            # Hilo para mostrar estadísticas periódicamente
            stats_thread = threading.Thread(target=self.show_stats)
            stats_thread.daemon = True
            stats_thread.start()
            
            while self.running:
                try:
                    client_socket, client_addr = self.proxy_socket.accept()
                    self.request_count += 1
                    print(f"\nNueva conexión desde {client_addr[0]}:{client_addr[1]}")
                    
                    # Crear hilo para manejar esta conexión
                    handler = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr)
                    )
                    handler.daemon = True
                    handler.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"Error aceptando conexión: {e}")
                        
        except KeyboardInterrupt:
            print("\n\nCerrando proxy...")
        except Exception as e:
            print(f"Error fatal: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el proxy"""
        self.running = False
        if self.proxy_socket:
            self.proxy_socket.close()
        print("Proxy cerrado")
    
    def show_stats(self):
        """Muestra estadísticas periódicas"""
        while self.running:
            time.sleep(30)
            if self.running:
                print(f"\nEstadísticas: {self.request_count} peticiones, {self.byte_count/1024:.1f} KB transferidos")
    
    def handle_client(self, client_socket, client_addr):
        """Maneja una conexión de cliente"""
        try:
            # Recibir la primera línea de la petición HTTP
            request_line = self.recv_line(client_socket)
            if not request_line:
                client_socket.close()
                return
            
            print(f"{request_line.strip()}")
            
            # Parsear la petición
            parts = request_line.split()
            if len(parts) < 3:
                client_socket.close()
                return
            
            method = parts[0].upper()
            url = parts[1]
            version = parts[2]
            
            # Manejar diferentes métodos
            if method == "CONNECT":
                # CONNECT se usa para HTTPS
                self.handle_connect(client_socket, url)
            else:
                # HTTP normal
                self.handle_http(client_socket, method, url, version)
                
        except Exception as e:
            print(f"Error manejando cliente {client_addr}: {e}")
        finally:
            client_socket.close()
    
    def recv_line(self, sock):
        """Recibe una línea (hasta \r\n o \n)"""
        data = b""
        while True:
            try:
                char = sock.recv(1)
                if not char:
                    break
                data += char
                if data.endswith(b'\r\n') or data.endswith(b'\n'):
                    break
            except:
                break
        return data.decode('utf-8', errors='ignore')
    
    def recv_headers(self, sock):
        """Recibe todos los headers HTTP"""
        headers = {}
        while True:
            line = self.recv_line(sock)
            if not line or line == '\r\n' or line == '\n':
                break
            
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.strip()] = value.strip()
        
        return headers
    
    def handle_http(self, client_socket, method, url, version):
        """Maneja peticiones HTTP normales (GET, POST, etc.)"""
        try:
            # Parsear URL para obtener servidor destino
            if url.startswith('http://'):
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or 80
                path = parsed.path or '/'
                if parsed.query:
                    path += '?' + parsed.query
            else:
                # Asumir que es una petición relativa (necesita Host header)
                # Primero leer headers para obtener Host
                headers = self.recv_headers(client_socket)
                if 'Host' not in headers:
                    print("No se encontró header Host")
                    client_socket.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                    return
                
                host = headers['Host'].split(':')[0]
                port = 80
                if ':' in headers['Host']:
                    port = int(headers['Host'].split(':')[1])
                path = url
            
            print(f"   → Reenviando a {host}:{port}{path}")
            
            # Conectar al servidor destino
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(10)
            server_socket.connect((host, port))
            
            # Reconstruir y reenviar la petición
            request = f"{method} {path} {version}\r\n"
            # Reenviar headers (en un proxy real, podrías modificarlos)
            for key, value in headers.items():
                request += f"{key}: {value}\r\n"
            request += "\r\n"
            
            server_socket.send(request.encode())
            
            # Reenviar datos bidireccionalmente
            self.forward_data(client_socket, server_socket)
            
        except socket.timeout:
            print(f"Timeout conectando a {host}")
        except ConnectionRefusedError:
            print(f"Conexión rechazada por {host}:{port}")
        except Exception as e:
            print(f"Error en HTTP: {e}")
        finally:
            if 'server_socket' in locals():
                server_socket.close()
    
    def handle_connect(self, client_socket, url):
        """Maneja el método CONNECT para HTTPS"""
        try:
            # Parsear host y puerto
            parts = url.split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 443
            
            print(f"   Túnel HTTPS a {host}:{port}")
            
            # Conectar al servidor destino
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(30)
            server_socket.connect((host, port))
            
            # Enviar respuesta de conexión establecida
            client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            
            # Ahora establecer un túnel bidireccional
            self.forward_data_bidirectional(client_socket, server_socket)
            
        except Exception as e:
            print(f"Error en CONNECT: {e}")
            client_socket.send(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        finally:
            if 'server_socket' in locals():
                server_socket.close()
    
    def forward_data(self, client_socket, server_socket):
        """Reenvía datos en una dirección (cliente → servidor)"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                self.byte_count += len(data)
                server_socket.send(data)
        except:
            pass
    
    def forward_data_bidirectional(self, client_socket, server_socket):
        """Establece un túnel bidireccional entre cliente y servidor"""
        # Usar dos hilos para manejar ambas direcciones
        stop_event = threading.Event()
        
        def forward(source, dest, direction):
            """Reenvía datos de source a dest"""
            try:
                while not stop_event.is_set():
                    data = source.recv(4096)
                    if not data:
                        break
                    self.byte_count += len(data)
                    dest.send(data)
            except:
                pass
            finally:
                stop_event.set()
        
        # Hilos para ambas direcciones
        t1 = threading.Thread(target=forward, args=(client_socket, server_socket, "C→S"))
        t2 = threading.Thread(target=forward, args=(server_socket, client_socket, "S→C"))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        
        # Esperar a que termine (cuando una conexión se cierra)
        t1.join()
        t2.join()


class HTTPProxyWithLogging(HTTPProxy):
    """Extensión del proxy con logging detallado y modificación de headers"""
    
    def handle_http(self, client_socket, method, url, version):
        """Versión con logging detallado"""
        start_time = time.time()
        
        # Guardar para estadísticas
        client_addr = client_socket.getpeername()
        
        try:
            # Parsear URL
            if url.startswith('http://'):
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or 80
                path = parsed.path or '/'
                if parsed.query:
                    path += '?' + parsed.query
            else:
                headers = self.recv_headers(client_socket)
                if 'Host' not in headers:
                    raise ValueError("No Host header")
                host = headers['Host'].split(':')[0]
                port = 80
                path = url
            
            # Logging
            print(f"\n{method} {url}")
            print(f"   Cliente: {client_addr[0]}:{client_addr[1]}")
            print(f"   Destino: {host}:{port}{path}")
            
            # Conectar al servidor
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(10)
            server_socket.connect((host, port))
            
            # Reconstruir petición (podrías modificar headers aquí)
            request = f"{method} {path} {version}\r\n"
            
            # Añadir header X-Forwarded-For
            if 'headers' in locals():
                headers['X-Forwarded-For'] = client_addr[0]
                for key, value in headers.items():
                    request += f"{key}: {value}\r\n"
            request += "\r\n"
            
            server_socket.send(request.encode())
            
            # Reenviar respuesta al cliente
            response_data = b''
            while True:
                data = server_socket.recv(4096)
                if not data:
                    break
                response_data += data
                client_socket.send(data)
            
            # Logging de respuesta
            elapsed = time.time() - start_time
            print(f"   Respuesta: {len(response_data)} bytes en {elapsed:.2f}s")
            
        except Exception as e:
            print(f"   Error: {e}")
            elapsed = time.time() - start_time
            print(f" Tiempo hasta error: {elapsed:.2f}s")


def test_proxy():
    """Función de prueba simple"""
    print("Para probar el proxy:")
    print("   1. Ejecuta el proxy: python3 proxy.py")
    print("   2. Configura tu navegador para usar proxy localhost:8888")
    print("   3. O usa curl: curl --proxy localhost:8888 http://example.com")
    print()
    print(" El proxy mostrará todas las peticiones que pasen por él")


if __name__ == "__main__":
    # Crear y ejecutar proxy
    proxy = HTTPProxy(host='localhost', port=8888)
    
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\n Proxy detenido")
    except Exception as e:
        print(f" Error: {e}")