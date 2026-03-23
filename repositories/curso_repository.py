from sqlmodel import Session, select
from models.curso import Curso
from uuid import UUID

class CursoRepository: # Clase CursoRepository

    def __init__(self, session:Session):
        self.session = session

    def get_by_id(self, curso_id: UUID):
        return self.session.get(Curso, curso_id)

    def get_all(self):
        return self.session.exec(select(Curso)).all()

    def create(self, curso:Curso): # puede funcionar para crear o updatear
        self.session.add(curso)
        return curso
    
    def delete(self, curso:Curso):
        self.session.delete(curso)