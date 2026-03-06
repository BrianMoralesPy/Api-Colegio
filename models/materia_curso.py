from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from uuid import UUID, uuid4
from typing import Optional
from .curso import Curso
from .materia import Materia


class MateriaCurso(SQLModel, table=True):
    __tablename__ = "materia_curso"
    # Asegura que no se repita la misma materia en el mismo curso y ciclo lectivo
    __table_args__ = (UniqueConstraint("curso_id","materia_id","ciclo_lectivo",name="uq_curso_materia_ciclo"),)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    curso_id: UUID = Field(foreign_key="cursos.id", nullable=False)
    materia_id: UUID = Field(foreign_key="materias.id", nullable=False)
    ciclo_lectivo: int = Field(max_length=5, nullable=False)
    carga_horaria: int = Field(nullable=False)
    # Relaciones opcionalmente cargadas para facilitar consultas
    curso: Optional[Curso] = Relationship()
    materia: Optional[Materia] = Relationship()