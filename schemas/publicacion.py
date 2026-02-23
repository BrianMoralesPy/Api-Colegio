from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from models.enums import TipoPublicacion


class PublicacionOut(BaseModel): # Lo que sale al GET
    id: UUID
    curso_id: UUID
    materia_id: UUID
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

