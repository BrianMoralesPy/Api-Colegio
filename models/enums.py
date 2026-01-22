from enum import Enum
# lo que usamos aca y en todo donde estan los models son las tablas de las bases de datos y los enums que tambien estan en la base de datos
class PerfilUsuario(str, Enum):
    alumno = "alumno"
    profesor = "profesor"
    admin = "admin"

class EstadosAlumno(str, Enum):
    activo = "activo"
    egresado = "egresado"
    suspendido = "suspendido"
    pendiente = "pendiente"

class TiposContrato(str, Enum):
    planta = "planta"
    suplente = "suplente"
    interino = "interino"
