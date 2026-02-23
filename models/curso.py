from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.types import Enum as SAEnum
from sqlalchemy import Column
from models.enums import Turnos
from datetime import datetime

class Curso(SQLModel, table=True):
    __tablename__ = "cursos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    nombre: str = Field(max_length=100, nullable=False)
    turno: Turnos = Field(sa_column=Column(SAEnum(Turnos, name="turnos", native_enum=True), nullable=False)) 
    activo: bool = Field(default=False)
    nivel: Optional[str] = Field(max_length=50, nullable=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_modificacion: Optional[datetime] = None