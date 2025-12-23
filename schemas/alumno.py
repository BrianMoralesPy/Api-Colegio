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
    activo: bool
    observaciones: Optional[str]

    class Config:
        from_attributes = True
