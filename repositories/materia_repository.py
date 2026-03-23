from sqlmodel import Session, select
from models.materia import Materia
from uuid import UUID

class MateriaRepository: # Clase MateriaRepository

    def __init__(self, session:Session):
        self.session = session

    def get_by_id(self, materia_id: UUID):
        return self.session.get(Materia, materia_id)

    def get_all(self):
        return self.session.exec(select(Materia)).all()

    def create(self, materia:Materia): # puede funcionar para crear o updatear
        self.session.add(materia)
        return materia
    
    def delete(self, materia:Materia):
        self.session.delete(materia)
        self.session.commit()