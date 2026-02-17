from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import date
from typing import Optional
from models.enums import TiposContrato
import re
# Este schema se utiliza para la creación de un nuevo profesor, donde se requieren los campos nombre, apellido y edad, mientras que el perfil es opcional.
class ProfesorOut(BaseModel):
    id: UUID
    fecha_contratacion: Optional[date]
    titulo: Optional[str]
    especialidad: Optional[str]
    legajo: Optional[str]
    tipo_contrato: Optional[TiposContrato]
    activo: bool

    class Config:
        from_attributes = True

class ProfesorOutFull(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    edad: int
    perfil: Optional[str]
    fecha_contratacion: Optional[date]
    titulo: Optional[str]
    especialidad: Optional[str]
    legajo: Optional[str]
    tipo_contrato: Optional[TiposContrato]
    activo: bool

class  ProfesorUpdate(BaseModel):
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
