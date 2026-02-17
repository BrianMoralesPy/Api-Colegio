from pydantic import BaseModel , Field, field_validator
from uuid import UUID
from datetime import date
from models.enums import EstadosAlumno
from typing import Optional
import re
# Este schema se utiliza para la creación de un nuevo alumno, donde se requieren los campos nombre, apellido y edad, mientras que el perfil es opcional.
class AlumnoOut(BaseModel):
    id: UUID
    legajo: Optional[str]
    fecha_ingreso: Optional[date]
    estado: EstadosAlumno
    observaciones: Optional[str]
    activo: bool
    
    class Config:
        from_attributes = True
    

class AlumnoOutFull(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    edad: int
    perfil: Optional[str]
    foto_url: Optional[str] = None
    legajo: Optional[str]
    fecha_ingreso: Optional[date]
    estado: EstadosAlumno
    observaciones: Optional[str]
    activo: bool

class AlumnoUpdate(BaseModel):
    legajo: Optional[str] = Field(default=None,min_length=2,max_length=10,description="Legajo del alumno")
    fecha_ingreso: Optional[date] = None
    estado: Optional[EstadosAlumno] = None
    observaciones: Optional[str] = Field(default=None,max_length=255)
    activo: Optional[bool] = None

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


    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, value):
        if value is None:
            return value

        if value > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")

        return value
    
    @field_validator("observaciones")
    @classmethod
    def validar_observaciones(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Las observaciones no pueden estar vacías")

        return value






