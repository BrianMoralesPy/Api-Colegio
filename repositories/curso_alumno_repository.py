from sqlmodel import Session, select
from uuid import UUID
from sqlalchemy.orm import selectinload

from models.curso_alumno import CursoAlumno
from models.materia_curso import MateriaCurso
from models.alumno import Alumno

class CursoAlumnoRepository:

    def __init__(self, session: Session):
        self.session = session
    
    # --------- Básicos ---------
    def create(self, obj: CursoAlumno):
        self.session.add(obj)

    def delete(self, obj: CursoAlumno):
        self.session.delete(obj)

    def get_by_id(self, curso_alumno_id: UUID) -> CursoAlumno | None:
        return self.session.get(CursoAlumno, curso_alumno_id)
    # --------- Validación única ---------

    def get_by_unique_fields(self,alumno_id: UUID, curso_id: UUID,
                            ciclo_lectivo: int) -> CursoAlumno | None:

        statement = select(CursoAlumno).where(
                    CursoAlumno.alumno_id == alumno_id,
                    CursoAlumno.curso_id == curso_id,
                    CursoAlumno.ciclo_lectivo == ciclo_lectivo)
        return self.session.exec(statement).first()

    # --------- Consulta con filtros ---------

    def get_all_with_filters(self, curso_id: UUID | None = None,
                            ciclo_lectivo: int | None = None) -> list[CursoAlumno]:

        statement = select(CursoAlumno).options(
                    selectinload(CursoAlumno.curso),
                    selectinload(CursoAlumno.alumno)
                    .selectinload(Alumno.usuario))

        if curso_id:
            statement = statement.where(CursoAlumno.curso_id == curso_id)

        if ciclo_lectivo:
            statement = statement.where(CursoAlumno.ciclo_lectivo == ciclo_lectivo)

        return self.session.exec(statement).all()

    

    def esta_inscripto(self, materia_curso_id: UUID, alumno_id: UUID):
        return self.session.exec(select(CursoAlumno)
                .join(MateriaCurso, CursoAlumno.curso_id == MateriaCurso.curso_id)
                .where(MateriaCurso.id == materia_curso_id,
                        CursoAlumno.alumno_id == alumno_id)).first()