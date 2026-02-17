from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from configuration import supabase # Importa la instancia de Supabase desde el archivo de configuración
from configuration import get_current_user # Importa la función get_current_user para obtener el usuario autenticado a partir del token de acceso
from configuration import get_session # Importa la función get_session para obtener una sesión de base de datos
from models.usuario import Usuario
from models.alumno import Alumno
from models.profesor import Profesor
from schemas.auth import RegisterAlumno, RegisterProfesor, LoginSchema,ResetPasswordSchema
from schemas.usuario import UsuarioOut
from schemas.alumno import AlumnoOut
from schemas.profesor import ProfesorOut
from schemas.me import MeResponse
from models.enums import PerfilUsuario,EstadosAlumno
from models.historial_contrasenas import HistorialContrasenas
from configuration import hash_password
import uuid
from uuid import UUID,uuid4

router = APIRouter(prefix="/auth", tags=["Auth"]) # Crea un router de FastAPI con el prefijo "/auth" para agrupar las rutas relacionadas con la autenticación y asigna la etiqueta "Auth" para la documentación automática

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

    historial = HistorialContrasenas(user_id=user_id,contrasena_hasheada=hash_password(data.password))
    session.add(historial)
    
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
    
    historial = HistorialContrasenas(user_id=user_id,contrasena_hasheada=hash_password(data.password))
    session.add(historial)
    
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
        data["profesor"] = (ProfesorOut.model_validate(profesor) if profesor else None)

    return data

@router.post("/me/avatar") # ENDPOINT PARA SUBIR FOTO DE PERFIL
def upload_avatar(file: UploadFile = File(...),user=Depends(get_current_user),session: Session = Depends(get_session)):
    user_id = UUID(user["sub"])
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Formato de imagen no permitido")

    extension = file.filename.split(".")[-1]
    filename = f"{user_id}-{uuid4()}.{extension}"
    contents = file.file.read()
    
    try:
        supabase.storage.from_("fotos_perfil").upload(filename,contents,{"content-type": file.content_type})
    except Exception as e:
        raise HTTPException(400, str(e))
    
    public_url = supabase.storage.from_("fotos_perfil").get_public_url(filename)
    usuario = session.get(Usuario, user_id)
    
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    usuario.foto_url = public_url
    session.commit()

    return {"fotos_perfil_url": public_url}

@router.post("/reset-password") # ENDPOINT PARA RESETEAR CONTRASEÑA
def reset_password(data:ResetPasswordSchema):
    try:
        supabase.auth.admin.update_user_by_id(data.user_id,{"password": data.new_password})
    except Exception:
        raise HTTPException(status_code=400,detail="Error al actualizar la contraseña")

    return {"ok": True, "message": "Contraseña actualizada correctamente"}