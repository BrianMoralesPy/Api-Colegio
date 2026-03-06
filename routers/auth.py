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
    """
    Registrar un nuevo alumno en el sistema.

    Este endpoint realiza el proceso completo de registro:
    1. Crea el usuario en **Supabase Auth**.
    2. Registra los datos básicos del usuario en la tabla `Usuario`.
    3. Crea el registro correspondiente en la tabla `Alumno`.
    4. Guarda la contraseña hasheada en `HistorialContrasenas`.

    Parámetros:
    - **data (RegisterAlumno)**  
      Objeto que contiene la información necesaria para el registro:
        - nombre
        - apellido
        - edad
        - email
        - password

    - **session (Session)**  
      Sesión de base de datos inyectada mediante `Depends(get_session)`.

    Retorna:
    - **dict**
      {
        "ok": True,
        "user_id": UUID
      }

      Indica que el registro fue exitoso junto con el ID del nuevo usuario creado.

    Errores:
    - **400 Bad Request**: Si el email ya está registrado en Supabase Auth.
    """
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
    """
    Registrar un nuevo profesor en el sistema.

    Este endpoint realiza el proceso completo de registro:
    1. Crea el usuario en **Supabase Auth**.
    2. Registra los datos básicos en la tabla `Usuario` con perfil **profesor**.
    3. Crea el registro correspondiente en la tabla `Profesor`.
    4. Guarda la contraseña hasheada en `HistorialContrasenas`.

    Parámetros:
    - **data (RegisterProfesor)**  
      Objeto que contiene la información necesaria para registrar un profesor:
        - nombre
        - apellido
        - edad
        - email
        - password

    - **session (Session)**  
      Sesión de base de datos utilizada para persistir los datos.

    Retorna:
    - **dict**
      {
        "ok": True,
        "user_id": UUID
      }

      Indica que el registro fue exitoso junto con el ID del nuevo usuario creado.

    Errores:
    - **400 Bad Request**: Si el email ya está registrado en Supabase Auth.
    """
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
    """
    Verificar credenciales de acceso de un usuario.

    Este endpoint autentica a un usuario utilizando **Supabase Auth**.
    Si las credenciales son válidas, se devuelve un **access token** que
    deberá utilizarse para acceder a endpoints protegidos.

    Parámetros:
    - **data (LoginSchema)**  
      Contiene las credenciales del usuario:
        - email
        - password

    Proceso:
    1. Se envían las credenciales a Supabase Auth.
    2. Si son válidas, Supabase genera una sesión con un **access_token**.
    3. Se devuelve el token junto con información básica del usuario.

    Retorna:
    - **dict**
      {
        "access_token": str,
        "user": {
            "id": UUID,
            "email": str
        }
      }

    Errores:
    - **401 Unauthorized**: Si las credenciales son inválidas o no se puede iniciar sesión.
    """
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
    """
    Obtener información del usuario autenticado.

    Este endpoint devuelve los datos del usuario asociado al **token de acceso**
    utilizado en la solicitud.

    Dependiendo del perfil del usuario, también se incluyen los datos específicos
    de su rol:

    - Si es **alumno** → se devuelven los datos de la tabla `Alumno`
    - Si es **profesor** → se devuelven los datos de la tabla `Profesor`

    Parámetros:
    - **user**  
      Información del usuario extraída del token JWT mediante `get_current_user`.
      Generalmente contiene:
        - sub (user_id)
        - email

    - **session (Session)**  
      Sesión de base de datos utilizada para obtener la información del usuario.

    Retorna:
    - **MeResponse**

      Estructura que contiene:
      - información básica del usuario
      - información específica del rol (alumno o profesor)

    Errores:
    - **404 Not Found**: Si el usuario no está registrado en la base de datos local.
    """
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

@router.put("/me/foto_perfil")
def subir_foto_perfil_o_modificarla(file: UploadFile = File(...),user=Depends(get_current_user),
                                    session: Session = Depends(get_session)):
    """
    Subir o actualizar la foto de perfil del usuario autenticado.

    Este endpoint permite:
    - Subir una nueva foto de perfil.
    - Reemplazar la foto existente eliminando previamente la anterior
      del almacenamiento.

    Proceso:
    1. Se obtiene el usuario autenticado desde el token.
    2. Si el usuario ya tiene una foto de perfil, se elimina del storage.
    3. Se sube la nueva imagen al **Supabase Storage**.
    4. Se guarda la ruta del archivo en la base de datos.
    5. Se devuelve la URL pública de la imagen.

    Parámetros:
    - **file (UploadFile)**  
      Archivo de imagen enviado en la request.

    - **user**  
      Usuario autenticado obtenido del token.

    - **session (Session)**  
      Sesión de base de datos utilizada para actualizar la información del usuario.

    Retorna:
    - **dict**
      {
        "foto_perfil_url": str
      }

      URL pública de la foto de perfil almacenada.
    """
    user_id = user["sub"]
    usuario = session.get(Usuario, user_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    if usuario.ruta_foto:
        delete_old_avatar(supabase_admin, usuario.ruta_foto)

    avatar_path = upload_avatar_to_storage(supabase_admin, file, user_id)

    usuario.ruta_foto = avatar_path
    session.commit()

    foto_url = supabase_admin.storage.from_("fotos_perfil").get_public_url(avatar_path)

    return {"foto_perfil_url": foto_url}


@router.post("/reset-password") # ENDPOINT PARA RESETEAR CONTRASEÑA
def recuperar_contrasenia_usuario(data:ResetPasswordSchema, session: Session = Depends(get_session)):
    """
    Restablecer la contraseña de un usuario.

    Este endpoint permite actualizar la contraseña de un usuario
    utilizando el servicio **Supabase Auth Admin**.

    Proceso:
    1. Se actualiza la contraseña en Supabase Auth.
    2. Se guarda el nuevo hash en `HistorialContrasenas`.
    3. Se confirma la transacción en la base de datos.

    Parámetros:
    - **data (ResetPasswordSchema)**  
      Contiene:
        - user_id
        - new_password

    - **session (Session)**  
      Sesión de base de datos para registrar el historial de contraseñas.

    Retorna:
    - **dict**
      {
        "ok": True,
        "message": "Contraseña actualizada correctamente"
      }

    Errores:
    - **400 Bad Request**: Si ocurre un error durante la actualización de la contraseña.
    """
    try:
        supabase_admin.auth.admin.update_user_by_id(data.user_id, {"password": data.new_password})
        historial = HistorialContrasenas(user_id=data.user_id, contrasena_hasheada=hash_password(data.new_password))
        session.add(historial)
        session.commit()

    except Exception:
        raise HTTPException(status_code=400, detail="Error al actualizar la contraseña")

    return {"ok": True, "message": "Contraseña actualizada correctamente"}