from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from models.alumno import Alumno
from models.profesor import Profesor
from models.usuario import Usuario
from models.historial_contrasenas import HistorialContrasenas
from models.enums import PerfilUsuario, EstadosAlumno
from schemas.auth import RegisterAlumno, RegisterProfesor, ResetPasswordSchema
from schemas.auth import LoginSchema
from schemas.usuario import UsuarioOut
from schemas.alumno import AlumnoOut
from schemas.profesor import ProfesorOut
from infrastructure.supabase import supabase_admin, supabase_auth
from repositories.alumno_repository import AlumnoRepository
from repositories.profesor_repository import ProfesorRepository
from repositories.usuario_repository import UsuarioRepository
from repositories.historial_repository import HistorialContrasenasRepository
from core.security.hashing import hash_password
from infrastructure.storage import upload_avatar_to_storage, delete_old_avatar
import uuid


class AuthService:

    def __init__(self, session: Session):
        self.session = session
        self.usuario_repo = UsuarioRepository(session)
        self.alumno_repo = AlumnoRepository(session)
        self.profesor_repo = ProfesorRepository(session)
        self.historial_repo = HistorialContrasenasRepository(session)
    
    def register_alumno(self, data: RegisterAlumno):
        """
        Registrar un nuevo alumno en el sistema.

        Este metodo realiza el proceso completo de registro:
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
            auth_user = supabase_admin.auth.admin.create_user({
                "email": data.email,
                "password": data.password,
                "email_confirm": True
            })
        except Exception:
            raise HTTPException(400, "El email ya está registrado")

        user_id = uuid.UUID(auth_user.user.id)

        try:
            usuario = Usuario(
                            id=user_id,
                            nombre=data.nombre,
                            apellido=data.apellido,
                            edad=data.edad,
                            perfil=PerfilUsuario.alumno)

            alumno = Alumno(id=user_id, 
                            legajo=None, 
                            fecha_ingreso=None, 
                            estado=EstadosAlumno.pendiente, 
                            observaciones=None, 
                            activo=False)

            historial = HistorialContrasenas(
                                            user_id=user_id,
                                            contrasena_hasheada=hash_password(data.password))

            self.usuario_repo.create(usuario)
            self.session.flush() # para despues de la transaccion crear el alumno y el historial
            self.alumno_repo.create(alumno)
            self.historial_repo.create(historial)

            self.session.commit()

            return {"ok": True, "user_id": user_id}

        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

        
    
    def register_profesor(self, data: RegisterProfesor):
        """
        Registrar un nuevo profesor en el sistema.

        Este metodo realiza el proceso completo de registro:
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
            auth_user = supabase_admin.auth.admin.create_user({
                "email": data.email,
                "password": data.password,
                "email_confirm": True
            })
        except Exception:
            raise HTTPException(400, "El email ya está registrado")

        user_id = uuid.UUID(auth_user.user.id)

        try:
            usuario = Usuario(
                            id=user_id,
                            nombre=data.nombre,
                            apellido=data.apellido,
                            edad=data.edad,
                            perfil=PerfilUsuario.profesor)

            profesor = Profesor(
                                id=user_id,
                                titulo=None,
                                especialidad=None,
                                fecha_contratacion=None,
                                legajo=None,
                                tipo_contrato=None,
                                activo=False)

            historial = HistorialContrasenas(
                                            user_id=user_id,
                                            contrasena_hasheada=hash_password(data.password))

            self.usuario_repo.create(usuario)
            self.session.flush()
            self.profesor_repo.create(profesor)
            self.historial_repo.create(historial)

            self.session.commit()
            
            return {"ok": True, "user_id": user_id}
        
        except Exception:
            self.session.rollback()
            supabase_admin.auth.admin.delete_user(str(user_id))
            raise HTTPException(500, "Error al registrar profesor")

        
    
    def login(self, data: LoginSchema):
        """
        Login de acceso de un usuario.

        Este metodo autentica a un usuario utilizando **Supabase Auth**.
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
            respuesta = supabase_auth.auth.sign_in_with_password({
                "email": data.email,
                "password": data.password
            })
        except Exception:
            raise HTTPException(401, "Credenciales inválidas")

        if not respuesta.session:
            raise HTTPException(401, "No se pudo iniciar sesión")

        return {
            "access_token": respuesta.session.access_token,
            "user": {
                "id": respuesta.user.id,
                "email": respuesta.user.email
            }
        }
    
    def get_me(self, current_user):
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
        user_id = current_user["sub"]

        usuario = self.usuario_repo.get_by_id(user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no registrado")

        respuesta = {
            "usuario": UsuarioOut.model_validate(usuario)
        }

        if usuario.perfil == PerfilUsuario.alumno:
            alumno = self.alumno_repo.get_by_id(user_id)
            respuesta["alumno"] = (AlumnoOut.model_validate(alumno) if alumno else None)

        elif usuario.perfil == PerfilUsuario.profesor:
            profesor = self.profesor_repo.get_by_id(user_id)
            respuesta["profesor"] = (ProfesorOut.model_validate(profesor) if profesor else None)

        return respuesta
    
    def update_profile_photo(self, user_id: str, file: UploadFile):
        """
        Subir o actualizar la foto de perfil del usuario autenticado.

        Este metodo permite:
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
        usuario = self.usuario_repo.get_by_id(user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        try:
            # Eliminar foto anterior si existe
            if usuario.ruta_foto:
                delete_old_avatar(usuario.ruta_foto)

            avatar_path = upload_avatar_to_storage(file, user_id)

            usuario.ruta_foto = avatar_path
            self.session.commit()

            foto_url = supabase_admin.storage \
                .from_("fotos_perfil") \
                .get_public_url(avatar_path)

            return {"foto_perfil_url": foto_url}

        except Exception:
            self.session.rollback()
            raise HTTPException(500, "Error al actualizar foto de perfil")
    
    def reset_password(self, data: ResetPasswordSchema):
        """
        Restablecer la contraseña de un usuario.

        Este metodo permite actualizar la contraseña de un usuario
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
            supabase_admin.auth.admin.update_user_by_id(data.user_id,{"password": data.new_password})

            historial = HistorialContrasenas(user_id=data.user_id,
                                                contrasena_hasheada=hash_password(data.new_password))

            self.historial_repo.create(historial)
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise HTTPException(400, "Error al actualizar contraseña")

        return {"ok": True, "message": "Contraseña actualizada correctamente"}

