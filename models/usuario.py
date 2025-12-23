from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.types import Enum as SAEnum
import uuid
from models.enums import PerfilUsuario

class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: uuid.UUID = Field(primary_key=True)
    nombre: str
    apellido: str
    edad: int
    perfil: PerfilUsuario = Field(
        sa_column=Column(
            SAEnum(
                PerfilUsuario,
                name="perfiles",
                native_enum=True
            ),
            nullable=False
        )
    )
