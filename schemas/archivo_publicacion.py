from pydantic import BaseModel, model_validator, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

# Este schema se utiliza para la salida de datos de un archivo asociado a una publicación, incluyendo todos los campos relevantes.
class ArchivoPublicacionOut(BaseModel):
    id: UUID
    fecha_subida: datetime
    publicacion_id: UUID
    nombre_original: str
    ruta_archivo: str
    tipo_mime: str
    tamanio_bytes: int

    class Config:
        from_attributes = True
