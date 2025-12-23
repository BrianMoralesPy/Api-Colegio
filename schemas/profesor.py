from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional
from models.enums import TiposContrato


class ProfesorOut(BaseModel):
    id: UUID
    titulo: str
    especialidad: str
    fecha_contratacion: Optional[date]
    legajo: Optional[str]
    tipo_contrato: TiposContrato
    activo: bool
    observaciones: str

    class Config:
        from_attributes = True
