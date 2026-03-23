#core/config.py tiene las constantes y variables que necesita para acceder a la db, jwt, etc
from pydantic_settings import BaseSettings # Importa la clase BaseSettings de pydantic_settings
from typing import ClassVar

class Settings(BaseSettings): #  Define la clase Settings que hereda de BaseSettings
    SUPABASE_URL: str 
    SUPABASE_SERVICE_ROLE_KEY: str
    ANON_KEY: str
    DATABASE_URL: str
    SUPABASE_JWT_SECRET: str

    ALGORITHM: str = "HS256"
    BUCKET_NAME: str = "archivos"
    ALLOWED_TYPES: ClassVar[list[str]] = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    class Config:
        env_file = ".env"

settings = Settings()