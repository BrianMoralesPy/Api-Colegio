from pydantic import BaseModel
from typing import Optional


class CorreccionCreate(BaseModel):
    nota: float
    comentario_profesor: Optional[str] = None