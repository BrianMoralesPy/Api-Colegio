from enum import Enum

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
