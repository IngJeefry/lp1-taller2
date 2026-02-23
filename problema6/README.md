# Problema 6: Chat con Salas (Gestión de grupos)

**Conceptos clave**:

- Gestión de múltiples salas/canales
- Estados de usuario más complejos
- Comandos avanzados de chat
- Sincronización de estado entre hilos

**Requerimientos**:

- Sistema de salas con JOIN, LEAVE, CREATE
- Lista de usuarios por sala
- Mensajes privados entre usuarios
- Persistencia básica de salas

___________________________________________________

**Comandos del cliente**:
- /CREATE <sala>      → Crear nueva sala
- /JOIN <sala>        → Unirse a una sala
- /LEAVE              → Salir de la sala actual
- /LIST               → Listar salas disponibles
- /USERS              → Ver usuarios en la sala actual
- /MSG <usuario> <texto> → Mensaje privado
- /HELP               → Mostrar ayuda
- /EXIT               → Desconectarse

Sin comando → mensaje público a la sala actual