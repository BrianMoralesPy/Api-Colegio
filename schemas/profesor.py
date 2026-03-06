from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import date,datetime
from typing import Optional
from models.enums import TiposContrato,RolEnCurso,Turnos
import re
# Este schema se utiliza para la creación de un nuevo profesor, donde se requieren los 
# campos nombre, apellido y edad, mientras que el perfil es opcional.
class ProfesorOut(BaseModel): # Lo que sale al GET
    id: UUID
    fecha_contratacion: Optional[date]
    titulo: Optional[str]
    especialidad: Optional[str]
    legajo: Optional[str]
    tipo_contrato: Optional[TiposContrato]
    activo: bool

    class Config:
        from_attributes = True

class ProfesorOutFull(BaseModel): # Lo que sale al GET con toda la info del usuario
    id: UUID
    nombre: str
    apellido: str
    edad: int
    perfil: Optional[str]
    foto_url: Optional[str]
    fecha_contratacion: Optional[date]
    titulo: Optional[str]
    especialidad: Optional[str]
    legajo: Optional[str]
    tipo_contrato: Optional[TiposContrato]
    activo: bool

class  ProfesorUpdate(BaseModel): # Lo que entra al PUT, todos los campos son opcionales porque el profesor puede querer actualizar solo algunos
    fecha_contratacion: Optional[date] = None
    titulo: Optional[str] = Field(default=None, min_length=2, max_length=50)
    especialidad: Optional[str] = Field(default=None, min_length=2, max_length=50)
    legajo: Optional[str] = Field(default=None, min_length=2, max_length=10)
    tipo_contrato: Optional[TiposContrato] = None
    activo: Optional[bool] = None
    @field_validator("titulo", "especialidad")
    @classmethod
    def validar_texto(cls,value:Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", value):
            raise ValueError("Solo se permiten letras y espacios")
        
        return value.strip().title()

    @field_validator("legajo")
    @classmethod
    def validar_legajo(cls, value: str | None):
        if value is None:
            return value

        value = value.strip().upper()

        if not re.match(r"^[A-Z0-9]+$", value):
            raise ValueError("El legajo solo puede contener letras y números")

        if not re.search(r"[A-Z]", value):
            raise ValueError("El legajo debe contener al menos una letra")

        if not re.search(r"[0-9]", value):
            raise ValueError("El legajo debe contener al menos un número")

        return value

    
    @field_validator("fecha_contratacion")
    @classmethod
    def validar_fecha(cls, value):
        if value is None:
            return value

        if value > date.today():
            raise ValueError("La fecha de contratación no puede ser futura")

        return value
    
#Seccion de profesor en curso
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

class MateriaCursoBasic(BaseModel):
    id: UUID
    ciclo_lectivo: int
    carga_horaria: int

    curso: CursoBasic
    materia: MateriaBasic

    class Config:
        from_attributes = True
class UsuarioBasic(BaseModel):
    id: UUID
    nombre: str
    apellido: str

    class Config:
        from_attributes = True

class ProfesorBasic(BaseModel): # Lo que sale al GET
    id: UUID
    fecha_contratacion: Optional[date]
    titulo: Optional[str]
    especialidad: Optional[str]
    legajo: Optional[str]
    tipo_contrato: Optional[TiposContrato]
    activo: bool
    usuario: UsuarioBasic

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
class ProfesorCursoMateriaOutFull(BaseModel):
    id: UUID
    rol_en_curso: RolEnCurso
    fecha_asignacion: datetime

    profesor: ProfesorBasic
    materia_curso: MateriaCursoBasic

    class Config:
        from_attributes = True

class ProfesorEnCursoMateriaCreate(BaseModel):
    profesor_id: UUID
    materia_curso_id: UUID
    rol_en_curso: RolEnCurso = RolEnCurso.titular
    class Config:
        from_attributes = True

class ProfesorEnCursoMateriaBasic(BaseModel):
    id: UUID
    profesor_id: UUID
    materia_curso_id: UUID
    rol_en_curso: RolEnCurso
    

    class Config:
        from_attributes = True

