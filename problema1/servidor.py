#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Servidor
Objetivo: Crear un servidor TCP que acepte una conexión y intercambie mensajes básicos
"""

import socket
def servidor_basico():

# Definir la dirección y puerto del servidor
    HOST = 'localhost'  # '127.0.0.1' también funciona
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
    servidor.listen(1)
    print(f"Servidor escuchando en {HOST}:{PORT} ...")
    print("Servidor a la espera de conexiones ...")

# Aceptar una conexión entrante
# accept() bloquea hasta que llega una conexión
# conn: nuevo socket para comunicarse con el cliente
# addr: dirección y puerto del cliente
    conn, addr = servidor.accept()
    print(f"Conexión realizada por {addr}")

# Recibir datos del cliente (hasta 1024 bytes)
    datos = conn.recv(1024)
    print(f"Mensaje recibido: {datos.decode('utf-8')}")
    
# Enviar respuesta al cliente (convertida a bytes)
# sendall() asegura que todos los datos sean enviados
    respuesta = "¡Hola, cliente! Mensaje recibido correctamente"
    conn.sendall(respuesta.encode('utf-8'))
    print(f"Respuesta enviada: {respuesta}")

# Cerrar la conexión con el cliente
    conn.close()
    print("Conexión cerrada")

    servidor.close()
    print("Servidor finalizado")

if __name__ == "__main__":
    servidor_basico()
