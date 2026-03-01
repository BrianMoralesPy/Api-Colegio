from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.types import Enum as SAEnum
from sqlalchemy import Column
from models.enums import EstadosEntregas
from datetime import datetime

class Entrega(SQLModel, table=True):
    __tablename__ = "entregas"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    publicacion_id: UUID = Field(foreign_key="publicaciones.id")
    alumno_id: UUID = Field(foreign_key="alumnos.id")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None
    nota: Optional[float] = None
    comentario_profesor: Optional[str] = None
    estado: EstadosEntregas = Field(sa_column=Column(SAEnum(EstadosEntregas, name="estados_entrega", native_enum=True), 
                                                        nullable=False))
    corregido_por_id: Optional[UUID] = Field(foreign_key="usuarios.id", nullable=True)