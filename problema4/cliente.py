#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Cliente
Objetivo: Crear un cliente HTTP que realice una petición GET a un servidor web local
"""

import http.client

# Definir la dirección y puerto del servidor HTTP
HOST = 'localhost'
PORT = 8000 

def cliente_http_basico():
    try:

#  Crear una conexión HTTP con el servidor
# HTTPConnection permite establecer conexiones HTTP con servidores
        conexion = http.client.HTTPConnection(HOST, PORT)
        print(f"Conexión establecida con {HOST}:{PORT}")

#  Realizar una petición GET al path raíz ('/')
# request() envía la petición HTTP al servidor
# Primer parámetro: método HTTP (GET, POST, etc.)
# Segundo parámetro: path del recurso solicitado
        conexion.request("GET", "/")
        print(f"Petición GET / enviada")

# Obtener la respuesta del servidor
# getresponse() devuelve un objeto HTTPResponse con los datos de la respuesta
        respuesta = conexion.getresponse()
        print(f"Respuesta recibida: {respuesta.status} {respuesta.reason}")

# Leer el contenido de la respuesta
# read() devuelve el cuerpo de la respuesta en bytes
        contenido_bytes = respuesta.read()

# Decodificar los datos de bytes a string e imprimirlos
# decode() convierte los bytes a string usando UTF-8 por defecto
        contenido = contenido_bytes.decode('utf-8')
        
        print(f"\nContenido recibido ({len(contenido_bytes)} bytes):")
        print("-" * 50)
        print(contenido)
        print("-" * 50)
        
    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar al servidor en {HOST}:{PORT}")
        print("   ¿Está el servidor corriendo?")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
# Cerrar la conexión con el servidor
        if 'conexion' in locals():
            conexion.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    print("=== CLIENTE HTTP BÁSICO ===\n")
    cliente_http_basico()
