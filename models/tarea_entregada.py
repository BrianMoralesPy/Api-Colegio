from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class TareaEntregada(SQLModel, table=True):
    __tablename__ = "tareas_entregadas"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fecha_subida: datetime = Field(default_factory=datetime.utcnow)
    entrega_id: UUID = Field(foreign_key="entregas.id", nullable=False)
    nombre_original: str = Field(max_length=255, nullable=False)
    ruta_archivo: str = Field(max_length=500, nullable=False)
    tipo_mime: str = Field(max_length=100, nullable=False)
    tamanio_bytes: int = Field(nullable=False)
