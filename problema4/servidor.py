#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Servidor
Objetivo: Implementar un servidor web simple que responda peticiones HTTP GET
y sirva archivos estáticos comprendiendo headers HTTP
"""

import http.server
import socket

# Definir la dirección y puerto del servidor HTTP
HOST = 'localhost'
PORT = 8000 

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Manejador personalizado de peticiones HTTP.
    Hereda de SimpleHTTPRequestHandler que proporciona funcionalidad básica
    para servir archivos estáticos y manejar peticiones HTTP.
    
    SimpleHTTPRequestHandler incluye:
    - Servicio de archivos estáticos desde el directorio actual
    - Manejo de métodos HTTP GET y HEAD
    - Generación automática de listados de directorios
    - Headers HTTP básicos (Content-Type, Content-Length, etc.)
    """
    pass
    # Nota: Al no sobreescribir ningún método, se usa el comportamiento por defecto
    # que sirve archivos del directorio actual y genera listados de directorios

# Crear una instancia de servidor HTTP
# HTTPServer maneja las conexiones entrantes y delega el procesamiento
# de peticiones al manejador especificado (MyRequestHandler)
# Parámetros:
# - (HOST, PORT): Dirección y puerto donde escuchar
# - MyRequestHandler: Clase que manejará las peticiones HTTP
server = http.server.HTTPServer((HOST, PORT), MyRequestHandler)

print(f" Servidor HTTP iniciado en http://{HOST}:{PORT}")
print("Sirviendo archivos desde:", server.server_name)
print("Presiona Ctrl+C para detener el servidor")

try:

# Iniciar el servidor y ponerlo en ejecución continua
# serve_forever() maneja peticiones indefinidamente hasta una interrupción
# (normalmente con Ctrl+C en la terminal)
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServidor detenido por el usuario")
except Exception as e:
    print(f"\nError: {e}")
finally:
    server.server_close()
    print("Servidor cerrado correctamente")
