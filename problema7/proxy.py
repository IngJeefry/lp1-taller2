import socket
import select

def start_proxy(host='localhost', port=8888):
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy.bind((host, port))
    proxy.listen(5)
    print(f"Proxy en {host}:{port}")

    while True:
        client, addr = proxy.accept()
        print(f"\nCliente: {addr[0]}:{addr[1]}")
        
        # Leer petición
        data = client.recv(4096)
        if not data: 
            client.close()
            continue
            
        # Extraer host
        lines = data.split(b'\r\n')
        first_line = lines[0].decode()
        if 'CONNECT' in first_line:
            host = first_line.split()[1].split(':')[0]
            port = 443
        else:
            host = first_line.split()[1].split('/')[2].split(':')[0]
            port = 80
            
        print(f"→ {host}:{port}")
        
        # Conectar al servidor
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, port))
        
        # Enviar petición
        server.send(data)
        
        if 'CONNECT' in first_line:
            client.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        
        # Túnel bidireccional
        sockets = [client, server]
        while sockets:
            r, _, _ = select.select(sockets, [], [], 1)
            for s in r:
                other = server if s is client else client
                try:
                    d = s.recv(4096)
                    if not d:
                        sockets.remove(s)
                        s.close()
                        break
                    other.send(d)
                except:
                    sockets.remove(s)
                    s.close()
                    break

if __name__ == "__main__":
    start_proxy()