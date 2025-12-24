from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional
from models.enums import TiposContrato


class ProfesorOut(BaseModel):
    id: UUID
    titulo: Optional[str]
    especialidad: Optional[str]
    fecha_contratacion: Optional[date]
    legajo: Optional[str]
    tipo_contrato: Optional[TiposContrato]
    activo: bool

    class Config:
        from_attributes = True
