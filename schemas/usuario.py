from pydantic import BaseModel
from uuid import UUID
from models.enums import PerfilUsuario


class UsuarioOut(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    edad: int
    perfil: PerfilUsuario

    class Config:
        from_attributes = True
