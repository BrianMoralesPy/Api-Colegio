from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4


class MateriaCurso(SQLModel, table=True):
    __tablename__ = "materia_curso"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    curso_id: UUID = Field(foreign_key="curso_id", nullable=False)
    materia_id: UUID = Field(foreign_key="materia_id", nullable=False)
    ciclo_lectivo: int = Field(max_length=5, nullable=False)
    carga_horaria: int = Field(nullable=False)