from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

class Materia(SQLModel, table=True):
    __tablename__ = "materias"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False)
    codigo: str = Field(max_length=100, nullable=False)
    activa: bool = Field(default=False)
    descripcion: Optional[str] = Field(max_length=255, nullable=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_modificacion: Optional[datetime] = None