from sqlmodel import create_engine, Session 
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from supabase import create_client
import os
import bcrypt

""" Variables para conexion a Supabase y su base de datos Postgres de SUPABASE """
load_dotenv()  # Carga las variables de .env
supabase = create_client(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_SERVICE_ROLE_KEY")) # Cliente de Supabase
DATABASE_URL = os.getenv("DATABASE_URL") # Ejemplo: "postgresql://usuario:contraseña@localhost:5432/mi_base_de_datos"
engine = create_engine(DATABASE_URL, echo=True) # Crear motor de base de datos osea la conexión principal a la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Esto es una fábrica de sesiones. Cada vez que se llama a SessionLocal() se obtiene una nueva sesión conectada a la BD.

""" Variables para autenticación y manejo de contraseñas y manejo de JWT """
security = HTTPBearer() # Define el esquema de autenticación
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET") # Esta clave se utiliza para verificar la firma de los tokens JWT emitidos por Supabase.
ALGORITHM = "HS256"  # Algoritmo de firma utilizado para los tokens JWT. HS256 es un algoritmo de firma simétrica que utiliza una clave secreta para firmar y verificar los tokens.



def get_session():
    """
    Dependencia para FastAPI, Crea una sesión , la inyecta en el endpont 
    y cuando termina el request la cierra automaticamente
    YIELD convierte una función normal en un generador, lo que permite usarla como una dependencia en FastAPI. 
    FastAPI se encarga de llamar a esta función, obtener la sesión y luego cerrarla automáticamente después de que 
    se complete el request.
    """
    with Session(engine) as session:
        yield session 



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)): # Permite verificar el token y obtener los datos del usuarios
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    return payload

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt y devuelve el hash resultante como una cadena de texto.
    Args:
        password (str): La contraseña en texto plano que se desea hashear.
    Returns:
        str: El hash de la contraseña generado por bcrypt, decodificado a UTF-8
    """
    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")

def password_ya_usada(password: str, hashes: list[str]) -> bool:
    """
    Verifica si una contraseña en texto plano ya ha sido usada comparándola con una lista de hashes de contraseñas anteriores.
    Args:
        password (str): La contraseña en texto plano que se desea verificar.
        hashes (list[str]): Una lista de hashes de contraseñas anteriores contra los cuales se comparará la contraseña proporcionada.   
    Returns:
        bool: True si la contraseña ya ha sido usada (es decir, si coincide con alguno de los hashes proporcionados), False en caso contrario.
    """
    for h in hashes:
        if bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8")):
            return True
    return False
