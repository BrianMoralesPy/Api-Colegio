# core/security/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlmodel import Session
from core.config import settings
from core.database import get_session
from models.usuario import Usuario

security = HTTPBearer() # Define el esquema de autenticación
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
        payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=[settings.ALGORITHM], options={"verify_aud": False})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    usuario = session.get(Usuario, user_id)
    if not usuario:
        raise HTTPException(404, "Usuario no registrado en el sistema")

    return {"sub": usuario.id, "perfil": usuario.perfil}