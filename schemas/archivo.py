from pydantic import BaseModel, model_validator, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class ArchivoOut(BaseModel):
    id: UUID
    fecha_subida: datetime
    publicacion_id: UUID
    nombre_original: str
    ruta_archivo: str
    tipo_mime: str
    tamanio_bytes: int

    class Config:
        from_attributes = True
