# repositories/profesor_repository.py

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from models.profesor import Profesor
from uuid import UUID

class ProfesorRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, profesor_id: UUID):
        statement = (
            select(Profesor)
            .where(Profesor.id == profesor_id)
            .options(selectinload(Profesor.usuario))
        )
        return self.session.exec(statement).first()

    def get_all(self):
        statement = (
            select(Profesor)
            .options(selectinload(Profesor.usuario))
        )
        return self.session.exec(statement).all()

    def create(self, profesor: Profesor): # puede funcionar para crear o updatear
        self.session.add(profesor)
        return profesor 

    def delete(self, profesor: Profesor):
        self.session.delete(profesor)