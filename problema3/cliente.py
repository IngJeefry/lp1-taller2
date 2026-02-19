#!/usr/bin/env python3
"""
Problema 3: Chat simple con múltiples clientes - Cliente
Objetivo: Crear un cliente de chat que se conecte a un servidor y permita enviar/recibir mensajes en tiempo real
"""

import socket
import threading

# Configuración del servidor
HOST = 'localhost'
PORT = 9999

def receive_messages(client_socket):
    """
    Función ejecutada en un hilo separado para recibir mensajes del servidor
    de forma continua sin bloquear el hilo principal.
    """
    while True:
        try:
        # Recibir mensajes del servidor (hasta 1024 bytes) y decodificarlos
            message = client_socket.recv(1024).decode()
            if not message:
                print("\n[Servidor] Conexión cerrada por el servidor")
                break

        # Imprimir el mensaje recibido
            print(message)
        except ConnectionResetError:
            print("\n[Error] Conexión perdida con el servidor")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            break
    client_socket.close()
    print("Desconectado del chat")

def iniciar_cliente():
# Solicitar nombre de usuario al cliente
    client_name = input("Cuál es tu nombre? ")

# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

# Conectar el socket al servidor en la dirección y puerto especificados
        client_socket.connect((HOST, PORT))
        print(f"Conectado al servidor de chat en {HOST}:{PORT}")

# Enviar el nombre del cliente al servidor (codificado a bytes)
        client_socket.send(client_name.encode())
        confirmacion = client_socket.recv(1024).decode()
        print(f"[Servidor] {confirmacion}")

# Crear y iniciar un hilo para recibir mensajes del servidor
# target: función que se ejecutará en el hilo
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()

# Bucle principal en el hilo principal para enviar mensajes al servidor
        while True:
                try:
    # Solicitar mensaje al usuario por consola
                    message = input("Mensaje: ")

    # Codificar el mensaje a bytes y enviarlo al servidor
                    client_socket.send(message.encode())

                except KeyboardInterrupt:
                    print("\nSaliendo del chat...")
                    break
                except Exception as e:
                    print(f"Error al enviar mensaje: {e}")
                    break
                
    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar al servidor en {HOST}:{PORT}")
        print("¿Está el servidor corriendo?")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        # Cerrar el socket del cliente
        client_socket.close()
        print("Cliente cerrado")

if __name__ == "__main__":
    iniciar_cliente()
