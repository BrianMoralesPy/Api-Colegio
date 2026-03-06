from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.types import Enum as SAEnum
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from models.enums import EstadosAlumnosEnCurso
from .curso import Curso
from .alumno import Alumno
from .usuario import Usuario

class CursoAlumno(SQLModel, table=True):
    __tablename__ = "curso_alumno"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    alumno_id: UUID = Field(foreign_key="alumnos.id", nullable=False)
    curso_id: UUID = Field(foreign_key="cursos.id", nullable=False)
    ciclo_lectivo: int = Field(max_length=5, nullable=False)
    fecha_inicio: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)), default_factory=datetime.utcnow)
    fecha_fin : Optional[datetime] = None
    estado: EstadosAlumnosEnCurso = Field(sa_column=Column(SAEnum(EstadosAlumnosEnCurso, name="estados_alumno_en_curso",
                                                                                            native_enum=True), nullable=False))
    
    curso: Optional[Curso] = Relationship()
    alumno: Optional[Alumno] = Relationship()
