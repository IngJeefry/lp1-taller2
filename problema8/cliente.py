"""
Problema 8: Cliente Tic-Tac-Toe - Versión minimalista
"""

import socket
import threading
import sys

def recibir_mensajes(sock):
    """Hilo para recibir mensajes del servidor"""
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(f"\n{msg}")
                print("> ", end="", flush=True)
            else:
                break
        except:
            break

def main():
    sock = socket.socket()
    try:
        sock.connect(('localhost', 9999))
    except:
        print("❌ No se pudo conectar al servidor")
        return
    
    # Hilo para recibir mensajes
    threading.Thread(target=recibir_mensajes, args=(sock,), daemon=True).start()
    
    # Loop principal para enviar comandos
    try:
        while True:
            msg = input("> ")
            if msg.lower() == 'salir':
                break
            sock.send(f"{msg}\n".encode())
    except:
        pass
    finally:
        sock.close()
        print("👋 Desconectado")

if __name__ == "__main__":
    main()