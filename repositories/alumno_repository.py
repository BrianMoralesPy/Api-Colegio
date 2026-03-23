# repositories/alumno_repository.py

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from models.alumno import Alumno
from uuid import UUID

class AlumnoRepository: # Clase AlumnoRepository

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, alumno_id: UUID):
        statement = (
            select(Alumno)
            .where(Alumno.id == alumno_id)
            .options(selectinload(Alumno.usuario))
        )
        return self.session.exec(statement).first()

    def get_all(self):
        statement = (
            select(Alumno)
            .options(selectinload(Alumno.usuario))
        )
        return self.session.exec(statement).all()

    def create(self, alumno: Alumno): # puede funcionar para crear o updatear
        self.session.add(alumno)
        return alumno

    def delete(self, alumno: Alumno):
        self.session.delete(alumno)