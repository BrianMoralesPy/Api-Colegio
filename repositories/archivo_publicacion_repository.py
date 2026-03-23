from sqlalchemy.orm import Session
from models.archivo_publicacion import ArchivosPublicacion
from uuid import UUID
class ArchivoPublicacionRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, archivo_id: UUID):
        return self.session.get(ArchivosPublicacion, archivo_id)

    def create(self, archivo: ArchivosPublicacion):
        self.session.add(archivo)
        return archivo