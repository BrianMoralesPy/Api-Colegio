# repositories/historial_contrasenas_repository.py

from sqlmodel import Session, delete
from models.historial_contrasenas import HistorialContrasenas
from uuid import UUID

class HistorialContrasenasRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def create(self, historial: HistorialContrasenas):
        self.session.add(historial)
        return historial

    def delete_by_user_id(self, user_id: UUID):
        statement = (
            delete(HistorialContrasenas)
            .where(HistorialContrasenas.user_id == user_id)
        )
        self.session.exec(statement)
    
    