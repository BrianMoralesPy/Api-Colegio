from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class MateriaOut(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    activa: bool
    descripcion: str
    fecha_creacion: datetime
    fecha_modificacion: Optional[datetime] = None
    

    class Config:
        from_attributes = True


class MateriaCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    codigo: str = Field(...,max_length=10,min_length=3,pattern=r'^[A-Z0-9]+$')
    descripcion: str = Field(..., max_length=255)


class MateriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    codigo: Optional[str] = Field(None,max_length=10,min_length=3,pattern=r'^[A-Z0-9]+$')
    descripcion: Optional[str] = Field(None, max_length=255)
    activa: Optional[bool] = None