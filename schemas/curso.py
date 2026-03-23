from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from models.enums import Turnos


class CursoOut(BaseModel): # Este schema se utiliza para la salida de datos de un curso, incluyendo todos los campos relevantes.
    id: UUID
    nombre: str
    turno: Turnos
    activo: bool
    nivel: str
    fecha_creacion: datetime
    fecha_modificacion: Optional[datetime] = None
    

    class Config:
        from_attributes = True


class CursoCreate(BaseModel): # Este schema se utiliza para la creación de un nuevo curso, donde se requieren los campos nombre, turno y nivel, mientras que el campo activo es opcional y por defecto es True.
    nombre: str = Field(..., max_length=100)
    turno: Turnos = Field(...) # El turno es obligatorio y debe ser uno de los valores definidos en el enum Turnos
    nivel: str = Field(..., max_length=100)


class CursoUpdate(BaseModel):   # Este schema se utiliza para la actualización de un curso existente, donde todos los campos son opcionales para permitir actualizaciones parciales. El campo turno, 
                                # si se proporciona, debe ser uno de los valores definidos en el enum Turnos.
    nombre: Optional[str] = Field(None, max_length=100)
    turno: Optional[Turnos] = None
    activo: Optional[bool] = None
    nivel: Optional[str] = Field(None, max_length=100)
    fecha_modificacion: Optional[datetime] = None
    
    @field_validator("fecha_modificacion", mode="before")
    @classmethod
    def set_fecha_actual_si_null(cls, value):
        if value is None:
            return datetime.utcnow()
        return value