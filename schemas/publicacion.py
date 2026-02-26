from pydantic import BaseModel, model_validator, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from models.enums import TipoPublicacion


class PublicacionOut(BaseModel): # Lo que sale al GET 
    id: UUID
    materia_curso_id: UUID
    profesor_id: UUID
    titulo: str
    descripcion: str
    tipo: TipoPublicacion
    fecha_publicacion: datetime
    fecha_entrega: Optional[datetime] = None
    activa: bool

    class Config:
        from_attributes = True
    
class PublicacionCreate(BaseModel): # Lo que entra al POST 
    titulo: str
    descripcion: str
    tipo: TipoPublicacion
    fecha_entrega: datetime | None = None

    @model_validator(mode="after")
    def validar_logica_tarea(self):
        if self.tipo == TipoPublicacion.tarea and not self.fecha_entrega:
            raise ValueError("Las tareas deben tener fecha de entrega")

        if self.tipo != TipoPublicacion.tarea and self.fecha_entrega:
            raise ValueError("Solo las tareas pueden tener fecha de entrega")

        return self

class PublicacionUpdate(BaseModel):
    titulo: Optional[str] = Field(default=None, max_length=150)
    descripcion: Optional[str] = None
    tipo: Optional[TipoPublicacion] = None
    fecha_entrega: Optional[datetime] = None
    
    @model_validator(mode="after")
    def validar_update(self):
        if self.tipo == TipoPublicacion.tarea and not self.fecha_entrega:
            raise ValueError("Las tareas deben tener fecha de entrega")

        if self.tipo and self.tipo != TipoPublicacion.tarea and self.fecha_entrega:
            raise ValueError("Solo las tareas pueden tener fecha de entrega")

        return self

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, value):
        if value is None:
            return value

        value = value.strip()
        if not value:
            raise ValueError("El título no puede estar vacío")

        return value

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, value):
        if value is None:
            return value

        value = value.strip()
        if not value:
            raise ValueError("La descripción no puede estar vacía")

        return value