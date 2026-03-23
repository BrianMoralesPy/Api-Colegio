from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from uuid import UUID
from models.materia_curso import MateriaCurso

class MateriaCursoRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def create(self, obj: MateriaCurso):
        self.session.add(obj)

    def delete(self, obj: MateriaCurso):
        self.session.delete(obj)

    def get_by_id(self, materia_curso_id: UUID) -> MateriaCurso | None:
        return self.session.get(MateriaCurso, materia_curso_id)
    
    def get_by_unique_fields(self, curso_id: UUID, materia_id: UUID,
                            ciclo_lectivo: int) -> MateriaCurso | None:

        statement = select(MateriaCurso).where(
                                        MateriaCurso.curso_id == curso_id,
                                        MateriaCurso.materia_id == materia_id,
                                        MateriaCurso.ciclo_lectivo == ciclo_lectivo)

        return self.session.exec(statement).first()

    def get_all_with_filters(self, curso_id: UUID | None = None,
                            ciclo_lectivo: int | None = None) -> list[MateriaCurso]:

        statement = select(MateriaCurso).options(
                                        selectinload(MateriaCurso.curso),
                                        selectinload(MateriaCurso.materia))

        if curso_id:
            statement = statement.where(MateriaCurso.curso_id == curso_id)

        if ciclo_lectivo:
            statement = statement.where(MateriaCurso.ciclo_lectivo == ciclo_lectivo)

        return self.session.exec(statement).all()