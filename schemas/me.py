from pydantic import BaseModel
from schemas.usuario import UsuarioOut
from schemas.alumno import AlumnoOut
from schemas.profesor import ProfesorOut

# Este schema se utiliza para la respuesta del endpoint /me, donde se devuelve la información del usuario autenticado, incluyendo su perfil de alumno o profesor si corresponde.
class MeResponse(BaseModel):
    usuario: UsuarioOut # CLASE USUARIO
    alumno: AlumnoOut | None = None # CLASE ALUMNO
    profesor: ProfesorOut | None = None # CLASE PROFESOR
