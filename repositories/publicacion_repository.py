from sqlmodel import Session, select
from uuid import UUID
from models.publicacion import Publicacion
from models.archivo_publicacion import ArchivosPublicacion

class PublicacionRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, publicacion_id: UUID) -> Publicacion | None:
        return self.session.get(Publicacion, publicacion_id)

    def get_archivos(self, publicacion_id: UUID) -> list[ArchivosPublicacion]:
        return self.session.exec(select(ArchivosPublicacion)
                                .where(ArchivosPublicacion.publicacion_id == publicacion_id)
                                ).all()

    def create(self, publicacion: Publicacion) -> Publicacion:
        self.session.add(publicacion)
        return publicacion
    """ 
    def delete(self, publicacion: Publicacion):
        self.session.delete(publicacion) """

    def soft_delete(self, publicacion: Publicacion):
        publicacion.activa = False
        self.session.add(publicacion)