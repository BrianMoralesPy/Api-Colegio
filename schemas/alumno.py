from pydantic import BaseModel
from uuid import UUID
from datetime import date
from models.enums import EstadosAlumno
from typing import Optional


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
    legajo: Optional[str]
    fecha_ingreso: Optional[date]
    estado: EstadosAlumno
    observaciones: Optional[str]
    activo: bool

class AlumnoUpdate(BaseModel):
    legajo: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    estado: Optional[EstadosAlumno] = None
    activo: Optional[bool] = None
    observaciones: Optional[str] = None