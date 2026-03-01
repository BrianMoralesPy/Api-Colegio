from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from services.configuration import supabase_admin,supabase_auth, get_session, get_current_user, hash_password, upload_avatar_to_storage,delete_old_avatar
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
        auth_user = supabase_admin.auth.admin.create_user({"email": data.email,"password": data.password,"email_confirm": True})
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
        auth_user = supabase_admin.auth.admin.create_user({"email": data.email,"password": data.password,"email_confirm": True})
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
        respuesta = supabase_auth.auth.sign_in_with_password({"email": data.email,"password": data.password})
    except Exception:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not respuesta.session:
        raise HTTPException(status_code=401, detail="No se pudo iniciar sesión")
    # Devuelve el token de acceso y la información básica del usuario si las credenciales son correctas 
    return {"access_token": respuesta.session.access_token, "user": {"id": respuesta.user.id, "email": respuesta.user.email}} 

@router.get("/me", response_model=MeResponse) # Y ACA PONES EL TOKEN Y TE DEVUELVE EL USUARIO PARA MANEJAR LA SESION ACTUAL OSEA SI ENTRAS AL HOME, ETC
def obtener_datos_del_usuario_logueado(user=Depends(get_current_user), session: Session = Depends(get_session)) -> MeResponse:
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

@router.put("/me/foto_perfil") # ENDPOINT PARA SUBIR O MDIFICAR FOTO DE PERFIL, SE REQUIERE EL TOKEN
def subir_foto_perfil_o_modificarla(file: UploadFile = File(...), user=Depends(get_current_user), session: Session = Depends(get_session)):

    user_id = user["sub"]

    usuario = session.get(Usuario, user_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    # Borrar anterior usando path
    if usuario.ruta_foto:
        delete_old_avatar(supabase_admin, usuario.ruta_foto)

    # Subir nueva
    avatar_path = upload_avatar_to_storage(supabase_admin, file, user_id)

    # Guardar SOLO el path
    usuario.ruta_foto = avatar_path
    session.commit()

    # Generar signed URL para respuesta inmediata 
    signed_url = supabase_admin.storage.from_("fotos_perfil").create_signed_url(avatar_path, 600)["signedURL"]

    return {"foto_perfil_url": signed_url}


@router.post("/reset-password") # ENDPOINT PARA RESETEAR CONTRASEÑA
def recuperar_contrasenia_usuario(data:ResetPasswordSchema, session: Session = Depends(get_session)):
    try:
        supabase_admin.auth.admin.update_user_by_id(data.user_id, {"password": data.new_password})
        historial = HistorialContrasenas(user_id=data.user_id, contrasena_hasheada=hash_password(data.new_password))
        session.add(historial)
        session.commit()

    except Exception:
        raise HTTPException(status_code=400, detail="Error al actualizar la contraseña")

    return {"ok": True, "message": "Contraseña actualizada correctamente"}