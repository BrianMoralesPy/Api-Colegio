from pydantic import BaseModel
from typing import Optional


class CorreccionCreate(BaseModel): # Este schema se utiliza para la creación de una nueva corrección, donde se requieren los campos alumno_id, materia_curso_id, nota y comentario_profesor.
    nota: float
    comentario_profesor: Optional[str] = None