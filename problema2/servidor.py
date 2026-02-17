#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Servidor
Objetivo: Crear un servidor TCP que devuelva exactamente lo que recibe del cliente
"""

import socket

def servidor_echo():

# Definir la dirección y puerto del servidor
    HOST = 'localhost'
    PORT = 9999

# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enlazar el socket a la dirección y puerto especificados
    servidor.bind((HOST, PORT))

# Poner el socket en modo escucha
# El parámetro define el número máximo de conexiones en cola
    servidor.listen(3)
    print(F"Servidor echo escuchando en {HOST} : {PORT}")

# Bucle infinito para manejar múltiples conexiones (una a la vez)
    while True:

        print("Servidor a la espera de conexiones ...")
    
    # Aceptar una conexión entrante
    # accept() bloquea hasta que llega una conexión
    # conn: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
        conn, addr = servidor.accept()
        print(f"Conexión realizada por {addr}")

    # Recibir datos del cliente (hasta 1024 bytes)
        data = conn.recv(1024)

    # Si no se reciben datos, salir del bucle
        if not data:
            print("Cliente cerro conexion sin enviar datos")
            conn.close()
            break

    # Mostrar los datos recibidos (en formato bytes)
        print("Datos recibidos (bytes):", data)
        print("Datos recibidos (texto):", data.decode('utf-8'))
    
    #Enviar los mismos datos de vuelta al cliente (echo)
        print(f"Enviando echo: {data}")
        conn.sendall(data)

    # Cerrar la conexión con el cliente actual
        conn.close()
        print(f"Conexion con {addr} cerrada")

if __name__ == "__main__":
    try:
        servidor_echo()
    except KeyboardInterrupt:
        print("Servidor detenido por el usuario")
    except Exception as e:
        print(f"Error: {e}")
