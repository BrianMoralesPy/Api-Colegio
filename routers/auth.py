from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.supabase import supabase
from core.security import get_current_user
from core.database import get_session
from models.usuario import Usuario
from models.alumno import Alumno
from models.profesor import Profesor
from schemas.auth import RegisterAlumno, RegisterProfesor, RegisterAdmin, LoginSchema
from schemas.usuario import UsuarioOut
from schemas.alumno import AlumnoOut
from schemas.profesor import ProfesorOut
from schemas.me import MeResponse
from models.enums import PerfilUsuario,EstadosAlumno,TiposContrato
import uuid
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register/alumno")
def register_alumno(data: RegisterAlumno,session: Session = Depends(get_session)):
    try:
        auth_user = supabase.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True
        })
    except Exception:
        raise HTTPException(status_code=400,detail="El email ya está registrado")

    user_id = uuid.UUID(auth_user.user.id)
    usuario = Usuario(
        id=user_id,
        nombre=data.nombre,
        apellido=data.apellido,
        edad=data.edad,
        perfil=PerfilUsuario.alumno,
    )
    session.add(usuario)
    session.flush()
    
    alumno = Alumno(
        id=user_id,
        legajo=None,
        fecha_ingreso=None,
        estado=EstadosAlumno.pendiente,
        observaciones=None,
        activo=False
    )
    session.add(alumno)
    session.commit()
    return {"ok": True, "user_id": user_id}

@router.post("/register/profesor")
def register_profesor(data: RegisterProfesor,session: Session = Depends(get_session)):
    try:
        auth_user = supabase.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True
        })
    except Exception:
        raise HTTPException(status_code=400,detail="El email ya está registrado")

    user_id = uuid.UUID(auth_user.user.id)
    usuario = Usuario(
        id=user_id,
        nombre=data.nombre,
        apellido=data.apellido,
        edad=data.edad,
        perfil=PerfilUsuario.profesor
    )
    session.add(usuario)
    session.flush()
    
    profesor =  Profesor(
        id=user_id,
        titulo=None,
        especialidad=None,
        fecha_contratacion=None,
        legajo=None,
        tipo_contrato=None,
        activo=False
    )
    session.add(profesor)
    session.commit()
    return {"ok": True, "user_id": user_id}

@router.post("/verificar-credenciales") # VERIFICAR CREDENCIALES, ACA PONES MAIL Y CONTRASEÑA Y SI ESTA BIEN TE DEVUELVE EL TOKEN
def verificar_credenciales(data: LoginSchema):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    if not response.session:
        raise HTTPException(
            status_code=401,
            detail="No se pudo iniciar sesión"
        )

    return {
        "access_token": response.session.access_token,
        "user": {
            "id": response.user.id,
            "email": response.user.email
        }
    }

@router.get("/me", response_model=MeResponse) # Y ACA PONES EL TOKEN Y TE DEVUELVE EL USUARIO PARA MANEJAR LA SESION ACTUAL OSEA SI ENTRAS AL HOME, ETC
def me(user=Depends(get_current_user), session: Session = Depends(get_session)):
    usuario = session.get(Usuario, user["sub"])
    if not usuario:
        raise HTTPException(404, "Usuario no registrado")
    data = {
        "usuario": UsuarioOut.model_validate(usuario)
    }

    if usuario.perfil == PerfilUsuario.alumno:
        alumno = session.get(Alumno, usuario.id)
        data["alumno"] = (
            AlumnoOut.model_validate(alumno) if alumno else None
        )

    elif usuario.perfil == PerfilUsuario.profesor:
        profesor = session.get(Profesor, usuario.id)
        data["profesor"] = (
            ProfesorOut.model_validate(profesor) if profesor else None
        )

    return data








