from pydantic import BaseModel
from schemas.usuario import UsuarioOut
from schemas.alumno import AlumnoOut
from schemas.profesor import ProfesorOut


class MeResponse(BaseModel):
    usuario: UsuarioOut # CLASE USUARIO
    alumno: AlumnoOut | None = None # CLASE ALUMNO
    profesor: ProfesorOut | None = None # CLASE PROFESOR
