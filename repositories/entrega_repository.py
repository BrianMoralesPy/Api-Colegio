from sqlalchemy import select
from sqlmodel import Session
from models.entrega import Entrega
from uuid import UUID

class EntregaRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, entrega_id: UUID):
        return self.session.get(Entrega, entrega_id)

    def get_by_publicacion_y_alumno(self, publicacion_id: UUID, alumno_id: UUID):
        return self.session.exec(select(Entrega).where(Entrega.publicacion_id == publicacion_id,
                                Entrega.alumno_id == alumno_id)).first()

    def create(self, entrega):
        self.session.add(entrega)
        return entrega