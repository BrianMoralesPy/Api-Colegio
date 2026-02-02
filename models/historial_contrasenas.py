# models/password_history.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class HistorialContrasenas(SQLModel, table=True):
    __tablename__ = "historial_contrasenas"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="usuarios.id", index=True)

    contrasena_hasheada: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
