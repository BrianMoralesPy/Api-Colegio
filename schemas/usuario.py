from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from models.enums import PerfilUsuario
import re


class UsuarioOut(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    edad: int
    perfil: PerfilUsuario

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None,min_length=2,max_length=50)
    apellido: Optional[str] = Field(default=None,min_length=2,max_length=50)
    edad: Optional[int] = Field(default=None,ge=5,le=100)
    @field_validator("nombre", "apellido")
    @classmethod
    def solo_letras(cls,value:Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", value):
            raise ValueError("Solo se permiten letras y espacios")
        
        return value.strip().title()