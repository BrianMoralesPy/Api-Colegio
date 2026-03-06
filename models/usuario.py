from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.types import Enum as SAEnum
import uuid
from models.enums import PerfilUsuario
from datetime import datetime
# lo que usamos aca y en todo donde estan los models son las tablas de las bases de datos y los enums que tambien estan en la base de datos
class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: uuid.UUID = Field(primary_key=True)
    nombre: str
    apellido: str
    edad: int
    perfil: PerfilUsuario = Field(sa_column=Column(SAEnum(PerfilUsuario, name="perfiles", native_enum=True), nullable=False))
    ruta_foto: str | None = None
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)