# repositories/usuario_repository.py

from sqlmodel import Session
from models.usuario import Usuario
from uuid import UUID

class UsuarioRepository:

    def __init__(self, session:Session):
        self.session = session

    def get_by_id(self, user_id:UUID):
        return self.session.get(Usuario, user_id)

    def create(self, usuario:Usuario): # puede funcionar para crear o updatear
        self.session.add(usuario)
        return usuario 

    def delete(self, usuario:Usuario):
        self.session.delete(usuario)