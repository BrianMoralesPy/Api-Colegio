from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from uuid import UUID
from models.curso_profesor import CursoProfesor
from models.profesor import Profesor

class CursoProfesorRepository:

    def __init__(self, session: Session):
        self.session = session
    
    # --------- Básicos ---------
    def create(self, obj: CursoProfesor):
        self.session.add(obj)

    def delete(self, obj: CursoProfesor):
        self.session.delete(obj)

    def get_by_id(self, curso_profesor_id: UUID) -> CursoProfesor | None:
        return self.session.get(CursoProfesor, curso_profesor_id)

    # --------- Validación única ---------
    def get_by_unique_fields(self, profesor_id: UUID, materia_curso_id: UUID) -> CursoProfesor | None:
        statement = select(CursoProfesor).where(
            CursoProfesor.profesor_id == profesor_id,
            CursoProfesor.materia_curso_id == materia_curso_id
        )
        return self.session.exec(statement).first()

    # --------- Consulta con filtros ---------
    def get_all_with_filters(self, materia_curso_id: UUID | None = None) -> list[CursoProfesor]:
        statement = select(CursoProfesor).options(
            selectinload(CursoProfesor.materia_curso),
            selectinload(CursoProfesor.profesor).selectinload(Profesor.usuario)
        )
        if materia_curso_id:
            statement = statement.where(CursoProfesor.materia_curso_id == materia_curso_id)
        return self.session.exec(statement).all()

    def esta_asignado(self, materia_curso_id: UUID, profesor_id: UUID):
        return self.session.exec(
            select(CursoProfesor).where(CursoProfesor.materia_curso_id == materia_curso_id,
                                        CursoProfesor.profesor_id == profesor_id)).first()