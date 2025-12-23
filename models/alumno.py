from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date
from sqlalchemy import Column
from sqlalchemy.types import Enum as SAEnum
from models.enums import EstadosAlumno
import uuid

class Alumno(SQLModel, table=True):
    __tablename__ = "alumnos"

    id: uuid.UUID = Field(
        primary_key=True,
        foreign_key="usuarios.id"
    )

    legajo: Optional[str] = None
    fecha_ingreso: Optional[date] = None

    estado: Optional[EstadosAlumno] = Field(
        default=EstadosAlumno.pendiente,
        sa_column=Column(
            SAEnum(
                EstadosAlumno,
                name="estados_alumno",
                native_enum=True
            ),
            nullable=False
        )
    )

    observaciones: Optional[str] = None
    activo: bool = False
