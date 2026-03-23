# core/database.py
from sqlmodel import create_engine, Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.config import settings # Importa el archivo de configuración

engine = create_engine(settings.DATABASE_URL, echo=True) # Crear motor de base de datos

def get_session():
    """
    Dependencia para FastAPI, Crea una sesión de la base de datos, la inyecta en el endpont 
    y cuando termina el request la cierra automaticamente.
    YIELD convierte una función normal en un generador, lo que permite usarla como una dependencia en FastAPI. 
    FastAPI se encarga de llamar a esta función, obtener la sesión y luego cerrarla automáticamente después de que 
    se complete el request.
    """
    with Session(engine) as session:
        yield session