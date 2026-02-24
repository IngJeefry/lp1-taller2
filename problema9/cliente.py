"""
Cliente para sistema distribuido
"""

import socket

class Client:
    def __init__(self, balancer_host='localhost', balancer_port=8888):
        self.balancer_host = balancer_host
        self.balancer_port = balancer_port
    
    def send_command(self, cmd):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.balancer_host, self.balancer_port))
            sock.send(f"{cmd}\n".encode())
            
            response = sock.recv(4096).decode().strip()
            sock.close()
            return response
        except Exception as e:
            return f"ERROR: {e}"
    
    def run(self):
        print("="*10)
        print(" CLIENTE SISTEMA DISTRIBUIDO")
        print("="*10)
        print("Comandos: SET clave valor, GET clave, exit")
        
        while True:
            cmd = input("\n> ").strip()
            if cmd.lower() == 'exit':
                break
            if cmd:
                response = self.send_command(cmd)
                print(f"Respuesta: {response}")

if __name__ == "__main__":
    Client().run()