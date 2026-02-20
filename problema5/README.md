# Problema 5: Transferencia de Archivos (Upload/Download)

**Conceptos clave**:

- Manejo de datos binarios
- Protocolo custom para transferencia de archivos
- Control de flujo y buffers
- Comandos: UPLOAD, DOWNLOAD, LIST

**Requerimientos**:

- Implementar protocolo de comandos
- Manejar archivos grandes con buffers
- Validar integridad de archivos (checksum)
- Manejo seguro de rutas de archivos
____________________________________________________________________________

**Comandos del cliente**:
- UPLOAD <nombre> <tamaño> <checksum> → Subir archivo
- DOWNLOAD <nombre> → Descargar archivo
- LIST → Listar archivos disponibles
- EXIT → Desconectarse

**Formato de respuestas del servidor**:
- OK <mensaje>
- ERROR <mensaje>
- DATA <tamaño> <checksum> (seguido de los datos binarios)
