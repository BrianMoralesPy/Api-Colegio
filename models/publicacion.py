from sqlmodel import SQLModel, Field, Relationship
from typing import Optional,List
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import Enum as SAEnum
from models.enums import TipoPublicacion
from uuid import UUID,uuid4

class Publicacion(SQLModel, table=True):
    __tablename__ = "publicaciones"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    materia_curso_id: UUID = Field(foreign_key="materia_curso.id", nullable=False)
    profesor_id: UUID = Field(foreign_key="profesores.id", nullable=False)
    titulo: str = Field(max_length=150, nullable=False)
    descripcion: str = Field(nullable=False)
    tipo: TipoPublicacion = Field(sa_column=Column(SAEnum(TipoPublicacion, name="tipo_publicaciones", 
                                                                    native_enum=True), nullable=False))
    fecha_publicacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_entrega: Optional[datetime] = None  # solo si es tarea
    activa: bool = Field(default=True)