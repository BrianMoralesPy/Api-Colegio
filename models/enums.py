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
class TipoPublicacion(str, Enum):
    aviso = "aviso"
    tarea = "tarea"
    material = "material"

class RolEnCurso(str, Enum):
    titular = "titular"
    suplente = "suplente"
    ayudante = "ayudante"

class Turnos(str, Enum):
    mañana = "mañana"
    tarde = "tarde"
    noche = "noche"

class EstadosAlumnosEnCurso(str, Enum):
    cursando = "cursando"
    aprobado = "aprobado"
    reprobado = "reprobado"

class EstadosEntregas(str, Enum):
    entregado = "entregado"
    corregido = "corregido"
    vencido= "vencido"
