#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Cliente
Objetivo: Crear un cliente TCP que se conecte a un servidor e intercambie mensajes básicos
"""

import socket

def cliente_basico():

# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al servidor en la dirección y puerto especificados
    servidor_direccion = ('localhost', 9999)
    cliente.connect(servidor_direccion)
    print(f"[CLIENTE] Conectado a {servidor_direccion[0]} : {servidor_direccion[1]}")

# Enviar datos al servidor (convertidos a bytes)
# sendall() asegura que todos los datos sean enviados
    mensaje = "¡Hola, servidor!"
    cliente.sendall(mensaje.encode('utf-8'))
    print(f"[CLIENTE] Enviado: {mensaje}")

# Recibir datos del servidor (hasta 1024 bytes)
    datos = cliente.recv(1024)

# Decodificar e imprimir los datos recibidos
    respuesta = datos.decode('utf-8')
    print(f"[CLIENTE] Recibido: {respuesta}")

# Cerrar la conexión con el servidor
    cliente.close()
    print("[CLIENTE] Conexión cerrada")

if __name__ == "__main__":
    cliente_basico()

