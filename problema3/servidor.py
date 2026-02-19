#!/usr/bin/env python3
"""
Problema 3: Chat simple con múltiples clientes - Servidor
Objetivo: Crear un servidor de chat que maneje múltiples clientes simultáneamente usando threads
"""

import socket
import threading

# Definir la dirección y puerto del servidor
HOST = 'localhost'
PORT = 9999

# Lista para mantener todos los sockets de clientes conectados
clients = []

def handle_client(client_socket, client_name):
    """
    Maneja la comunicación con un cliente específico en un hilo separado.
    
    Args:
        client_socket: Socket del cliente
        client_name: Nombre del cliente
    """
    while True:
        try:
            # Recibir datos del cliente (hasta 1024 bytes)
            data = client_socket.recv(1024)

            # Si no se reciben datos, el cliente se desconectó
            if not data:
                break
                
            # Formatear el mensaje con el nombre del cliente
            message = f"{client_name}: {data.decode()}"
            
            # Imprimir el mensaje en el servidor
            print(message)
            
            # Retransmitir el mensaje a todos los clientes excepto al remitente
            broadcast(message, client_socket)
            
        except ConnectionResetError:
            # Manejar desconexión inesperada del cliente
            print(f"Cliente {client_name} se desconectó inesperadamente")
            break
        except Exception as e:
            print(f"Error con cliente {client_name}: {e}")
            break
        
    if client_socket in clients:
            clients.remove(client_socket)
    client_socket.close()
    print(f"Cliente {client_name} desconectado")
    broadcast(f"{client_name} ha abandonado el chat.", None)
            #break

def broadcast(message, sender_socket):
    """
    Envía un mensaje a todos los clientes conectados excepto al remitente.
    
    Args:
        message: Mensaje a enviar (string)
        sender_socket: Socket del cliente que envió el mensaje original
    """
    for client in clients:
        if client != sender_socket:
            # Enviar el mensaje codificado a bytes a cada cliente
            try:
                client.send(message.encode())
            except:
                # Si hay error al enviar, probablemente el cliente se desconectó
                clients.remove(client)
                client.close()

def iniciar_servidor():
# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enlazar el socket a la dirección y puerto especificados
    servidor.bind((HOST, PORT))

# Poner el socket en modo escucha
# El parámetro define el número máximo de conexiones en cola
    servidor.listen(5)
    print("Servidor a la espera de conexiones ...")

# Bucle principal para aceptar conexiones entrantes
    while True:
        try:
    # Aceptar una conexión entrante
    # client: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
            client, addr = servidor.accept()
            print(f"Conexión realizada por {addr}")
    
    # Recibir el nombre del cliente (hasta 1024 bytes) y decodificarlo
            client_name = client.recv(1024).decode()
            print(f"Cliente {client_name} conectado desde {addr}")

    # Agregar el socket del cliente a la lista de clientes conectados
            clients.append(client)
    # Enviar mensaje de confirmación de conexión al cliente
            client.send("ya estás conectado!".encode())
    
    # Notificar a todos los clientes que un nuevo usuario se unió al chat
            broadcast(f"{client_name} se ha unido al Chat.", client)
    
    # Crear e iniciar un hilo para manejar la comunicación con este cliente
    # target: función que se ejecutará en el hilo
    # args: argumentos que se pasarán a la función
            client_handler = threading.Thread(target=handle_client, args=(client, client_name))
            client_handler.daemon = True
            client_handler.start()
        
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario")
            break
        except Exception as e:
            print(f"Error en el servidor: {e}")
            break
    
    # Limpiar antes de cerrar
    print("Cerrando servidor...")
    for client in clients:
        client.close()
    servidor.close()

if __name__ == "__main__":
    iniciar_servidor()

