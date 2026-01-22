from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional
from models.enums import TiposContrato


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

class ProfesorUpdate(BaseModel):
    fecha_contratacion: Optional[date] = None
    titulo: Optional[str] = None
    especialidad: Optional[str] = None
    legajo: Optional[str] = None
    tipo_contrato: Optional[TiposContrato] = None
    activo: Optional[bool] = None
