from sqlmodel import SQLModel, Field
import uuid
from datetime import date
from typing import Optional
from sqlalchemy import Column
from sqlalchemy.types import Enum as SAEnum
from models.enums import TiposContrato
# lo que usamos aca y en todo donde estan los models son las tablas de las bases de datos y los enums que tambien estan en la base de datos
class Profesor(SQLModel, table=True):
    __tablename__ = "profesores"

    id: uuid.UUID = Field(primary_key=True,foreign_key="usuarios.id")
    titulo: str
    especialidad: str
    fecha_contratacion: Optional[date] = None
    legajo: Optional[str] = None
    tipo_contrato: TiposContrato = Field(sa_column=Column(SAEnum(TiposContrato,name="tipos_contrato", native_enum=True),nullable=True))
    activo: bool = False
