from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.types import Enum as SAEnum
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from models.enums import RolEnCurso

class CursoProfesor(SQLModel, table=True):
    __tablename__ = "curso_profesor"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    materia_curso_id: UUID = Field(foreign_key="materia_curso.id", nullable=False)
    profesor_id: UUID = Field(foreign_key="profesores.id", nullable=False)
    rol_en_curso: RolEnCurso = Field(sa_column=Column(SAEnum(RolEnCurso, name="roles_profesor_en_curso", native_enum=True), 
                                                                                                        nullable=False))
    fecha_asignacion: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)),default_factory=datetime.utcnow)