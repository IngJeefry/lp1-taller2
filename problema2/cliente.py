#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Cliente
Objetivo: Crear un cliente TCP que envíe un mensaje al servidor y reciba la misma respuesta
"""

import socket

def cliente_echo():

# Definir la dirección y puerto del servidor
    HOST = 'localhost'
    PORT = 9999

# Solicitar mensaje al usuario por consola
    message = input("Mensaje: ")

# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        # Conectar el socket al servidor en la dirección y puerto especificados
        cliente.connect((HOST, PORT))
        print(f"Conectado al servidor {HOST}:{PORT}")

        # Mostrar mensaje que se va a enviar
        print(f"Mensaje '{message}' enviado.")

        # Codificar el mensaje a bytes y enviarlo al servidor
        # sendall() asegura que todos los datos sean enviados
        cliente.sendall(message.encode('utf-8'))
        print(f"Mensaje enviado: {message}")

        # Recibir datos del servidor (hasta 1024 bytes)
        data = cliente.recv(1024)

        # Decodificar e imprimir los datos recibidos
        respuesta = data.decode('utf-8')
        print(f"Mensaje recibido: ", data.decode())

    except ConnectionRefusedError:
        print("Error: No se pudo conectar al servidor. ¿Está corriendo?")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:

        # Cerrar la conexión con el servidor
        cliente.close()
        print("Conexión cerrada")
    
if __name__ == "__main__":
    cliente_echo()
