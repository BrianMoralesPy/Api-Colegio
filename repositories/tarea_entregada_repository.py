from sqlalchemy.orm import Session
from models.tarea_entregada import TareaEntregada
from uuid import UUID
class TareaEntregadaRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, archivo_id: UUID):
        return self.session.get(TareaEntregada, archivo_id)

    def create(self, tarea: TareaEntregada):
        self.session.add(tarea)
        return tarea