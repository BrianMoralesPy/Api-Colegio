from fastapi import APIRouter, Depends, UploadFile, File # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.auth import get_current_user
from schemas.auth import RegisterAlumno, RegisterProfesor, LoginSchema,ResetPasswordSchema
from schemas.me import MeResponse
from core.security.permissions import require_role
from models.enums import PerfilUsuario
from services.auth_service import AuthService
router = APIRouter(prefix="/auth", tags=["Auth"])   # Crea un router de FastAPI con el prefijo "/auth" para 
                                                    # agrupar las rutas relacionadas con la autenticación y asigna la 
                                                    # etiqueta "Auth" para la documentación automática

@router.post("/register/alumno")
def register_alumno(data: RegisterAlumno,session: Session = Depends(get_session)):
    auth_service = AuthService(session)
    return auth_service.register_alumno(data)

@router.post("/register/profesor")
def register_profesor(data: RegisterProfesor,session: Session = Depends(get_session)):
    auth_service = AuthService(session)
    return auth_service.register_profesor(data)

@router.post("/login")
def login(data: LoginSchema):
    auth_service = AuthService(None)
    return auth_service.login(data)

@router.get("/me", response_model=MeResponse)
def me(user=Depends(get_current_user),session: Session = Depends(get_session)):
    auth_service = AuthService(session)
    return auth_service.get_me(user)

@router.put("/me/foto_perfil")
def subir_foto_perfil(file: UploadFile = File(...), user=Depends(get_current_user),
                    session: Session = Depends(get_session)):
    auth_service = AuthService(session)
    return auth_service.update_profile_photo(user["sub"], file)

@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema,session: Session = Depends(get_session) ,
                    user=Depends(require_role(PerfilUsuario.admin))):
    auth_service = AuthService(session)
    return auth_service.reset_password(data)