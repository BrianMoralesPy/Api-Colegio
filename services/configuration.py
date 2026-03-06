from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import create_engine, Session 
from supabase import create_client
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError
from dotenv import load_dotenv
from uuid import uuid4
from models.usuario import Usuario
from models.enums import PerfilUsuario
import os
import bcrypt

""" Variables para conexion a Supabase y su base de datos Postgres de SUPABASE """
load_dotenv()  # Carga las variables de .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ANON_KEY = os.getenv("ANON_KEY")
DATABASE_URL = os.getenv("DATABASE_URL") # Ejemplo: "postgresql://usuario:contraseña@localhost:5432/mi_base_de_datos"

supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) # Cliente de Supabase admin
supabase_auth = create_client(SUPABASE_URL,ANON_KEY) # Cliente de Supabase para autenticación de usuarios (registro, login, etc)
engine = create_engine(DATABASE_URL, echo=True) # Crear motor de base de datos osea la conexión principal a la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Esto es una fábrica de sesiones. Cada vez que se llama a SessionLocal() se obtiene una nueva sesión conectada a la BD.

""" Variables para autenticación y manejo de contraseñas y manejo de JWT """
security = HTTPBearer() # Define el esquema de autenticación
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET") # Esta clave se utiliza para verificar la firma de los tokens JWT emitidos por Supabase.
ALGORITHM = "HS256"  # Algoritmo de firma utilizado para los tokens JWT. HS256 es un algoritmo de firma simétrica que utiliza una clave secreta para firmar y verificar los tokens.
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
BUCKET_NAME = "archivos" # Nombre del bucket en Supabase donde se almacenan los archivos de las publicaciones

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



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    """
    Dependencia para FastAPI que se encarga de autenticar al usuario a través del token JWT proporcionado en el 
    encabezado de autorización. Verifica la validez del token, decodifica su contenido para obtener el ID del 
    usuario, y luego consulta la base de datos para obtener la información del usuario correspondiente. 
    Si el token es inválido, ha expirado, o el usuario no existe en la base de datos, se lanzan excepciones  
    apropiadas.
    Args:
    credentials: (HTTPAuthorizationCredentials): Las credenciales de autorización extraídas del encabezado de la 
    solicitud, que incluyen el token JWT.
    session: (Session): La sesión de base de datos proporcionada por la dependencia get_session.
    Returns:
    dict: Un diccionario que contiene el ID del usuario autenticado y su perfil, extra
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], options={"verify_aud": False})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Token inválido")

    usuario = session.get(Usuario, user_id)
    if not usuario:
        raise HTTPException(404, "Usuario no registrado en el sistema")

    return {"sub": usuario.id, "perfil": usuario.perfil}


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

def upload_avatar_to_storage(supabase_admin, file: UploadFile, user_id, bucket_name: str = "fotos_perfil"):
    """
    Sube una foto de perfil al almacenamiento de Supabase.
    Args:
        supabase_admin: La instancia del cliente de Supabase con permisos administrativos.
        file (UploadFile): El archivo de imagen que se desea subir.
        user_id (str): El ID del usuario al que pertenece la foto de perfil.
        bucket_name (str): El nombre del bucket en Supabase donde se almacenará la foto. Por defecto es "fotos_perfil".
    Returns:
        str: La ruta interna del archivo subido en el bucket de Supabase.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Formato de imagen no permitido")

    extension = file.filename.split(".")[-1].lower()
    filename = f"usuarios/{user_id}/{uuid4().hex}.{extension}"

    contents = file.file.read()

    try:
        supabase_admin.storage.from_(bucket_name).upload(filename,contents,{"content-type": file.content_type})
    except Exception as e:
        raise HTTPException(400, str(e))

    # ⚠️ Devolver solo el path interno
    return filename

def delete_old_avatar(supabase_admin, avatar_path: str, bucket_name: str = "fotos_perfil"):
    """
    Elimina una foto de perfil anterior del almacenamiento de Supabase dado su URL pública.
    Args:
        supabase: La instancia del cliente de Supabase.
        public_url (str): La URL pública de la foto de perfil que se desea eliminar.
        bucket_name (str): El nombre del bucket en Supabase donde se almacenan las fotos de perfil. Por defecto es "fotos_perfil".
    """
    try:
        supabase_admin.storage.from_(bucket_name).remove([avatar_path])
    except Exception as e:
        print("Error al eliminar foto anterior:", str(e))

def upload_file_to_storage(path: str, file):
    """
    Sube un archivo al almacenamiento de Supabase en la ruta especificada.
    Args:
        path (str): La ruta dentro del bucket de Supabase donde se desea almacenar el archivo, por ejemplo "publicaciones/{publicacion_id}/archivo.pdf".
        file: El archivo que se desea subir, generalmente un objeto UploadFile de FastAPI.
    """
    content = file.file.read()

    response = supabase_admin.storage.from_(BUCKET_NAME).upload(path, content, {"content-type": file.content_type,
                                            "x-upsert": "false"})
    if hasattr(response, "error") and response.error:
        raise Exception(f"Error al subir archivo: {response.error}")

def generate_signed_url(path: str, expires_in: int = 3600):
    """
    Genera una URL temporal firmada para acceder a un archivo privado.
    expires_in: segundos de validez
    """
    response = supabase_admin.storage.from_("archivos").create_signed_url(path, expires_in)
    if hasattr(response, "error") and response.error:
        raise Exception("Error al generar signed URL")

    return response.get("signedURL")

def require_role(required_role: PerfilUsuario):
    """
    Dependencia de FastAPI que verifica si el usuario autenticado tiene el rol requerido para acceder a un endpoint específico.
    Args:        required_role (PerfilUsuario): El rol requerido para acceder al endpoint, definido en el enum PerfilUsuario.
    Returns:        function: Una función que se puede usar como dependencia en FastAPI para proteger endpoints según el rol del usuario.
    Comportamiento:        - La función interna role_checker se encarga de verificar el rol del usuario autenticado.        - Si el perfil del 
    usuario no coincide con el rol requerido, se lanza una excepción HTTP 403 Forbidden.        
    - Si el usuario tiene el rol adecuado, se devuelve la información del usuario para su uso en el endpoint protegido.
    Uso:        - Se utiliza como una dependencia en los endpoints de FastAPI para restringir el acceso según el rol del usuario. Por ejemplo:    
    @router.get("/admin-only", dependencies=[Depends(require_role(PerfilUsuario.admin))])        def admin_only_endpoint():            return {"message": "Solo los administradores pueden ver esto"}
    """
    def role_checker(user=Depends(get_current_user)):
        if user["perfil"] != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="No tienes permisos suficientes")
        return user
    return role_checker