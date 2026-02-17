from sqlmodel import create_engine, Session 
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from supabase import create_client
from uuid import uuid4
from urllib.parse import urlparse
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
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]


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

def upload_avatar_to_storage(supabase, file: UploadFile, user_id, bucket_name: str = "fotos_perfil"):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Formato de imagen no permitido")

    extension = file.filename.split(".")[-1].lower()

    filename = f"usuarios/{user_id}/{uuid4().hex}.{extension}"

    contents = file.file.read()

    try:
        supabase.storage.from_(f"{bucket_name}").upload(filename,contents,{"content-type": file.content_type})
    except Exception as e:
        raise HTTPException(400, str(e))

    public_url = supabase.storage.from_(f"{bucket_name}").get_public_url(filename)

    return public_url

def delete_old_avatar(supabase, public_url: str, bucket_name: str = "fotos_perfil"):
    """
    Elimina una foto de perfil anterior del almacenamiento de Supabase dado su URL pública.
    Args:
        supabase: La instancia del cliente de Supabase.
        public_url (str): La URL pública de la foto de perfil que se desea eliminar.
        bucket_name (str): El nombre del bucket en Supabase donde se almacenan las fotos de perfil. Por defecto es "fotos_perfil".
    """
    try: 
        parsed = urlparse(public_url)
        path = parsed.path.split(f"/{bucket_name}/")[-1]
        supabase.storage.from_(bucket_name).remove([path])
    except Exception as e:
        print("Error al eliminar foto anterior:", str(e))

