from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from configuration import supabase, get_session, get_current_user, hash_password, upload_avatar_to_storage,delete_old_avatar
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
import uuid
from uuid import UUID
""" 
En el  archivo Auth manejamos basicamente el registro de usuarios (alumnos y profesores), el login para obtener el token de acceso, 
la ruta /me para obtener la información del usuario autenticado y la ruta para subir foto de perfil. También se incluye 
un endpoint para resetear la contraseña. no manejamos por completo la tabla Alumnos ni Profesores, le asignamos campos vacios
que luego se pueden completar desde el panel de administración. El objetivo es que el usuario pueda registrarse y luego un admin
pueda completar su perfil y aprobar su cuenta para que pueda acceder a las funcionalidades de la app. 
"""
router = APIRouter(prefix="/auth", tags=["Auth"])   # Crea un router de FastAPI con el prefijo "/auth" para 
                                                    # agrupar las rutas relacionadas con la autenticación y asigna la 
                                                    # etiqueta "Auth" para la documentación automática

@router.post("/register/alumno")
def register_alumno(data: RegisterAlumno, session: Session = Depends(get_session)) -> dict:
    try:
        auth_user = supabase.auth.admin.create_user({"email": data.email,"password": data.password,"email_confirm": True})
    except Exception:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user_id = uuid.UUID(auth_user.user.id)
    usuario = Usuario(id=user_id, nombre=data.nombre, apellido=data.apellido, edad=data.edad, perfil=PerfilUsuario.alumno)
    session.add(usuario)
    session.flush()
    
    alumno = Alumno(id=user_id, legajo=None, fecha_ingreso=None, estado=EstadosAlumno.pendiente, observaciones=None, activo=False)
    session.add(alumno)

    historial = HistorialContrasenas(user_id=user_id, contrasena_hasheada=hash_password(data.password))
    session.add(historial)  
    
    session.commit()
    
    return {"ok": True, "user_id": user_id} # Devuelve una respuesta indicando que el registro fue exitoso y el ID del nuevo usuario creado

@router.post("/register/profesor")
def register_profesor(data: RegisterProfesor, session: Session = Depends(get_session)) -> dict:
    try:
        auth_user = supabase.auth.admin.create_user({"email": data.email,"password": data.password,"email_confirm": True})
    except Exception:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user_id = uuid.UUID(auth_user.user.id)
    usuario = Usuario(id=user_id,nombre=data.nombre,apellido=data.apellido,edad=data.edad,perfil=PerfilUsuario.profesor)
    session.add(usuario)
    session.flush()
    
    profesor =  Profesor(id=user_id,titulo=None,especialidad=None,fecha_contratacion=None,legajo=None,tipo_contrato=None,activo=False)
    session.add(profesor)
    historial = HistorialContrasenas(user_id=user_id, contrasena_hasheada=hash_password(data.password))
    
    session.add(historial)
    session.commit()
    
    return {"ok": True, "user_id": user_id} # Devuelve una respuesta indicando que el registro fue exitoso y el ID del nuevo usuario creado

@router.post("/verificar-credenciales") # VERIFICAR CREDENCIALES, ACA PONES MAIL Y CONTRASEÑA Y SI ESTA BIEN TE DEVUELVE EL TOKEN
def verificar_credenciales(data: LoginSchema):
    try:
        respuesta = supabase.auth.sign_in_with_password({"email": data.email,"password": data.password})
    except Exception:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not respuesta.session:
        raise HTTPException(status_code=401, detail="No se pudo iniciar sesión")
    # Devuelve el token de acceso y la información básica del usuario si las credenciales son correctas 
    return {"access_token": respuesta.session.access_token, "user": {"id": respuesta.user.id, "email": respuesta.user.email}} 

@router.get("/me", response_model=MeResponse) # Y ACA PONES EL TOKEN Y TE DEVUELVE EL USUARIO PARA MANEJAR LA SESION ACTUAL OSEA SI ENTRAS AL HOME, ETC
def me(user=Depends(get_current_user), session: Session = Depends(get_session)) -> MeResponse:
    usuario = session.get(Usuario, user["sub"]) # OBTIENE EL USUARIO DE LA BASE DE DATOS UTILIZANDO EL ID OBTENIDO DEL TOKEN DE ACCESO
    if not usuario:
        raise HTTPException(404, "Usuario no registrado")
    data = {"usuario": UsuarioOut.model_validate(usuario)} 

    if usuario.perfil == PerfilUsuario.alumno:
        alumno = session.get(Alumno, usuario.id)
        data["alumno"] = (AlumnoOut.model_validate(alumno) if alumno else None)

    elif usuario.perfil == PerfilUsuario.profesor:
        profesor = session.get(Profesor, usuario.id)
        data["profesor"] = (ProfesorOut.model_validate(profesor) if profesor else None)

    return data # Devuelve la información del usuario autenticado, incluyendo su perfil y datos específicos según su rol (alumno o profesor)

@router.post("/me/avatar") # ENDPOINT PARA SUBIR FOTO DE PERFIL
def upload_avatar(file: UploadFile = File(...), user=Depends(get_current_user), session: Session = Depends(get_session)) -> dict:
    user_id = UUID(user["sub"])

    usuario = session.get(Usuario, user_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    # Borrar foto anterior si existe
    if usuario.foto_url:
        delete_old_avatar(supabase, usuario.foto_url)
    # Subir nueva
    public_url = upload_avatar_to_storage(supabase, file, user_id)  # Sube la nueva foto de perfil al almacenamiento de Supabase y 
                                                                    # obtiene la URL pública de la imagen subida
    # Guardar en DB
    usuario.foto_url = public_url
    session.commit()

    return {"foto_perfil_url": public_url}  # Devuelve la URL pública de la nueva foto de perfil después de subirla y actualizar el registro 
                                            # del usuario en la base de datos


@router.post("/reset-password") # ENDPOINT PARA RESETEAR CONTRASEÑA
def reset_password(data:ResetPasswordSchema, session: Session = Depends(get_session)):
    try:
        supabase.auth.admin.update_user_by_id(data.user_id, {"password": data.new_password})
        historial = HistorialContrasenas(user_id=data.user_id, contrasena_hasheada=hash_password(data.new_password))
        session.add(historial)
        session.commit()

    except Exception:
        raise HTTPException(status_code=400, detail="Error al actualizar la contraseña")

    return {"ok": True, "message": "Contraseña actualizada correctamente"}