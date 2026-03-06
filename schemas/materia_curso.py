from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional
from models.enums import Turnos

class CursoBasic(BaseModel):
    id: UUID
    nombre: str
    turno: Turnos
    nivel: str

    class Config:
        from_attributes = True

class MateriaBasic(BaseModel):
    id: UUID
    nombre: str
    codigo: str
    descripcion: str

    class Config:
        from_attributes = True

class MateriaCursoOutStandar(BaseModel):
    id: UUID
    curso_id: UUID
    materia_id: UUID
    ciclo_lectivo: int
    carga_horaria: int

    class Config:
        from_attributes = True
        
class MateriaCursoOutFull(BaseModel):
    id: UUID
    ciclo_lectivo: int
    carga_horaria: int

    curso: CursoBasic
    materia: MateriaBasic

    class Config:
        from_attributes = True


class MateriaCursoCreate(BaseModel):
    curso_id: UUID
    materia_id: UUID
    ciclo_lectivo: int = Field(..., ge=2000, le=2100)
    carga_horaria: int = Field(..., gt=0)

    @field_validator("ciclo_lectivo")
    def validar_anio(cls, value):
        if value < 2000:
            raise ValueError("El ciclo lectivo debe ser un año válido")
        return value
