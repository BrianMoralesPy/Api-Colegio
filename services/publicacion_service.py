from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session

from models.enums import EstadosEntregas
from models.usuario import Usuario
from models.publicacion import Publicacion
from models.entrega import Entrega
from models.tarea_entregada import TareaEntregada
from models.archivo_publicacion import ArchivosPublicacion
from schemas.publicacion import PublicacionCreate, PublicacionOut, PublicacionUpdate
from schemas.archivo_publicacion import ArchivoPublicacionOut
from schemas.entregas import CorreccionCreate

from repositories.publicacion_repository import PublicacionRepository
from repositories.materia_curso_repository import MateriaCursoRepository
from repositories.curso_profesor_repository import CursoProfesorRepository
from repositories.curso_alumno_repository import CursoAlumnoRepository
from repositories.archivo_publicacion_repository import ArchivoPublicacionRepository
from repositories.tarea_entregada_repository import TareaEntregadaRepository
from repositories.entrega_repository import EntregaRepository

from services.storage_service import StorageService
from permissions.publicacion_permissions import PublicacionPermission


class PublicacionService:

    def __init__(self, session: Session):
        self.session = session

        # repositories
        self.publicacion_repo = PublicacionRepository(session)
        self.archivo_publicacion_repo = ArchivoPublicacionRepository(session)
        self.entrega_repo = EntregaRepository(session)
        self.tarea_entregada_repo = TareaEntregadaRepository(session)
        self.materia_curso_repo = MateriaCursoRepository(session)
        self.curso_profesor_repo = CursoProfesorRepository(session)
        self.curso_alumno_repo = CursoAlumnoRepository(session)

        # permissions
        self.permission = PublicacionPermission(self.curso_profesor_repo,
                                                self.curso_alumno_repo)
        
    def leer_publicacion(self, publicacion_id: UUID, user_id: UUID):
        """
        Metodo para obtener la información de una publicación específica.

        El acceso se controla según el perfil del usuario:

        - ADMIN:
            Puede ver cualquier publicación, incluso si está inactiva.

        - PROFESOR:
            Puede ver todas las publicaciones que haya creado.
            También puede ver publicaciones activas de otras materias.
            No puede ver publicaciones inactivas creadas por otros profesores.

        - ALUMNO:
            Puede ver publicaciones activas de las materias en las que esté inscripto.
            No puede ver publicaciones inactivas.

        Args:
            publicacion_id (UUID):
                ID de la publicación que se desea consultar.

            user:
                Usuario autenticado obtenido desde el token JWT mediante la dependencia get_current_user.

            session (Session):
                Sesión de base de datos proporcionada por la dependencia get_session.

        Returns:
            PublicacionOut:
                Objeto con la información completa de la publicación.

        Raises:
            HTTPException:
                404 si el usuario o la publicación no existen.
                403 si el usuario no tiene permisos para acceder a la publicación.
                500 si ocurre un error interno.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        publicacion = self.publicacion_repo.get_by_id(publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        if not self.permission.puede_ver_publicacion(usuario, publicacion):
            raise HTTPException(403, "No autorizado")

        return publicacion
    
    def leer_archivos(self, publicacion_id: UUID, user_id: UUID):
        """
        Metodo para obtener los archivos adjuntos de una publicación.

        Permite recuperar todos los archivos asociados a una publicación
        de tipo tarea o material.

        Control de acceso:

        - ADMIN:
            Puede ver los archivos de cualquier publicación.

        - PROFESOR:
            Puede ver archivos de publicaciones pertenecientes a materias
            en las que esté asignado como profesor.

        - ALUMNO:
            Puede ver archivos de publicaciones activas de materias
            en las que esté inscripto.

        Args:
            publicacion_id (UUID):
                ID de la publicación de la cual se desean obtener los archivos.

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            list[ArchivoPublicacionOut]:
                Lista de archivos asociados a la publicación.

        Raises:
            HTTPException:
                404 si el usuario o la publicación no existen.
                403 si el usuario no tiene acceso a la materia.
                500 si ocurre un error interno.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        publicacion = self.publicacion_repo.get_by_id(publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        if not self.permission.puede_ver_publicacion(usuario, publicacion):
            raise HTTPException(403, "No autorizado")

        return self.publicacion_repo.get_archivos(publicacion_id)

    def crear_publicacion(self,materia_curso_id: UUID,data: PublicacionCreate,
                            user_id: UUID):
        """
        Metodo para crear una nueva publicación dentro de una materia de un curso.

        Tipos de publicación posibles:
        - aviso
        - tarea
        - material

        Control de acceso:

        - ADMIN:
            No puede crear publicaciones.

        - PROFESOR:
            Puede crear publicaciones únicamente en materias donde esté asignado.

        - ALUMNO:
            No puede crear publicaciones.

        Args:
            materia_curso_id (UUID):
                ID de la relación materia-curso donde se creará la publicación.

            data (PublicacionCreate):
                Datos necesarios para crear la publicación
                (título, descripción, tipo, fecha de entrega, etc.).

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            PublicacionOut:
                Objeto con la información de la publicación creada.

        Raises:
            HTTPException:
                404 si la materia del curso no existe.
                403 si el usuario no tiene permiso para publicar.
                500 si ocurre un error interno durante la creación.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        materia_curso = self.materia_curso_repo.get_by_id(materia_curso_id)
        if not materia_curso:
            raise HTTPException(404, "Materia del curso no encontrada")

        if not self.permission.puede_crear_publicacion(usuario, materia_curso_id):
            raise HTTPException(403, "No autorizado")

        nueva_publicacion = Publicacion(
            materia_curso_id=materia_curso_id,
            profesor_id=usuario.id,
            activa=True,
            fecha_publicacion=datetime.now(timezone.utc),
            **data.model_dump())
        
        self.publicacion_repo.create(nueva_publicacion)
        self.session.commit()
        self.session.refresh(nueva_publicacion)

        return PublicacionOut.model_validate(nueva_publicacion)
    
    def subir_archivo(self, publicacion_id: UUID, file, user_id: UUID):
        """
        Metodo para subir archivos adjuntos a una publicación.

        Solo permite subir archivos a publicaciones de tipo:
        - tarea
        - material

        Los archivos se almacenan en Supabase Storage y se registra
        su metadata en la base de datos.

        Control de acceso:

        - ADMIN:
            No puede subir archivos.

        - PROFESOR:
            Puede subir archivos únicamente en publicaciones que haya creado
            o en materias donde esté asignado.

        - ALUMNO:
            No puede subir archivos.

        Args:
            publicacion_id (UUID):
                ID de la publicación a la cual se adjuntará el archivo.

            file (UploadFile):
                Archivo enviado mediante formulario multipart/form-data.

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            ArchivoPublicacionOut:
                Información del archivo subido.

        Raises:
            HTTPException:
                404 si la publicación no existe.
                400 si la publicación es de tipo aviso.
                403 si el usuario no tiene permiso.
                500 si ocurre un error al subir el archivo.
        """
        try:

            usuario = self.session.get(Usuario, user_id)
            if not usuario:
                raise HTTPException(404, "Usuario no encontrado")

            publicacion = self.publicacion_repo.get_by_id(publicacion_id)
            if not publicacion:
                raise HTTPException(404, "Publicación no encontrada")

            if not self.permission.puede_subir_archivo(usuario, publicacion):
                raise HTTPException(403, "No autorizado")

            # generar ruta
            ruta_storage = StorageService.generar_ruta_publicacion(publicacion_id,
                                                            publicacion.tipo.value,
                                                            file.filename)

            # subir a storage
            StorageService.subir(ruta_storage, file)

            nuevo_archivo = ArchivosPublicacion(fecha_subida=datetime.now(timezone.utc),
                                                publicacion_id=publicacion_id,
                                                nombre_original=file.filename,
                                                ruta_archivo=ruta_storage,
                                                tipo_mime=file.content_type,
                                                tamanio_bytes=file.size or 0,)

            self.archivo_publicacion_repo.create(nuevo_archivo)
            self.session.commit()
            self.session.refresh(nuevo_archivo)
            return ArchivoPublicacionOut.model_validate(nuevo_archivo)

        except Exception as e:
            raise HTTPException(500, f"Error al subir el archivo: {e}")
    
    def entregar_tarea(self, publicacion_id: UUID, file, user_id: UUID):
        """
        Metodo para que un alumno entregue una tarea.

        Permite subir un archivo asociado a una publicación de tipo tarea.
        El archivo se almacena en Supabase Storage y se registra en la base de datos.

        Control de acceso:

        - ADMIN:
            No puede entregar tareas.

        - PROFESOR:
            No puede entregar tareas.

        - ALUMNO:
            Puede entregar tareas únicamente si:
            - La publicación es de tipo tarea.
            - La tarea no está vencida.
            - El alumno pertenece al curso de la materia.

        Args:
            publicacion_id (UUID):
                ID de la publicación de tipo tarea.

            file (UploadFile):
                Archivo enviado por el alumno como entrega.

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            dict:
                Mensaje confirmando que la entrega fue realizada correctamente.

        Raises:
            HTTPException:
                404 si la publicación no existe.
                400 si la tarea está vencida o no es del tipo correcto.
                403 si el alumno no pertenece al curso.
                500 si ocurre un error interno.
        """
        try:
            usuario = self.session.get(Usuario, user_id)
            if not usuario:
                raise HTTPException(404, "Usuario no encontrado")

            publicacion = self.publicacion_repo.get_by_id(publicacion_id)
            if not publicacion:
                raise HTTPException(404, "Publicación no encontrada")

            if not self.permission.puede_entregar_tarea(usuario, publicacion):
                raise HTTPException(403, "No autorizado para entregar esta tarea")

            entrega = self.entrega_repo.get_by_publicacion_y_alumno(
                publicacion_id,
                usuario.id)

            if not entrega:
                entrega = Entrega(
                    publicacion_id=publicacion_id,
                    alumno_id=usuario.id,
                    fecha_creacion=datetime.now(timezone.utc),
                    estado=EstadosEntregas.entregado)
                
                self.entrega_repo.create(entrega)
                self.session.flush()  # importante para obtener entrega.id sin commit

            else:
                entrega.fecha_actualizacion = datetime.now(timezone.utc)
                entrega.estado = EstadosEntregas.entregado

            ruta_storage = StorageService.generar_ruta_entrega(publicacion_id,
                                                                usuario.id,
                                                                file.filename)

            StorageService.subir(ruta_storage, file)

            tarea_entregada = TareaEntregada(
                entrega_id=entrega.id,
                nombre_original=file.filename,
                ruta_archivo=ruta_storage,
                tipo_mime=file.content_type,
                tamanio_bytes=file.size or 0
            )

            self.tarea_entregada_repo.create(tarea_entregada)

            self.session.commit()

            return {"message": "Entrega realizada correctamente"}

        except:
            self.session.rollback()
            raise

    def corregir_entrega(self, entrega_id: UUID, datos: CorreccionCreate, user_id: UUID):
        """
        Metodo para que un profesor corrija una entrega de tarea.

        Permite asignar:
        - nota
        - comentario del profesor

        Control de acceso:

        - ADMIN:
            No puede corregir entregas.

        - PROFESOR:
            Puede corregir entregas únicamente de materias
            en las que esté asignado.

        - ALUMNO:
            No puede corregir entregas.

        Args:
            entrega_id (UUID):
                ID de la entrega que se desea corregir.

            datos (CorreccionCreate):
                Información de la corrección (nota y comentario).

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            Entrega:
                Objeto actualizado con la corrección aplicada.

        Raises:
            HTTPException:
                404 si la entrega no existe.
                400 si la entrega ya fue corregida.
                403 si el profesor no pertenece a la materia.
                500 si ocurre un error interno.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(401, "Usuario no encontrado")

        entrega = self.entrega_repo.get_by_id(entrega_id)
        if not entrega:
            raise HTTPException(404, "Entrega no encontrada")

        publicacion = self.publicacion_repo.get_by_id(entrega.publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        if not self.permission.puede_corregir_entrega(usuario, entrega, publicacion):
            raise HTTPException(403, "No autorizado para corregir esta entrega")

        entrega.nota = datos.nota
        entrega.comentario_profesor = datos.comentario_profesor
        entrega.fecha_actualizacion = datetime.now(timezone.utc)
        entrega.corregido_por_id = usuario.id
        entrega.estado = EstadosEntregas.corregido

        self.session.commit()
        self.session.refresh(entrega)

        return entrega
    
    def actualizar_publicacion(self, publicacion_id: UUID, data:PublicacionUpdate, user_id: UUID):
        """
        Metodo para actualizar una publicación existente.

        Solo se actualizarán los campos enviados en la request,
        permitiendo un comportamiento similar a PATCH.

        Control de acceso:

        - ADMIN:
            No puede actualizar publicaciones.

        - PROFESOR:
            Puede actualizar únicamente publicaciones que haya creado.

        - ALUMNO:
            No puede actualizar publicaciones.

        Args:
            publicacion_id (UUID):
                ID de la publicación que se desea modificar.

            data (PublicacionUpdate):
                Datos que se desean actualizar.

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            PublicacionUpdate:
                Información actualizada de la publicación.

        Raises:
            HTTPException:
                404 si la publicación no existe.
                403 si el usuario no tiene permisos.
                500 si ocurre un error durante la actualización.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        publicacion = self.publicacion_repo.get_by_id(publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        if not self.permission.puede_actualizar_publicacion(usuario, publicacion):
            raise HTTPException(403, "No autorizado para modificar")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(publicacion, key, value)

        publicacion.fecha_actualizacion = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(publicacion)

        return publicacion
    
    def eliminar_publicacion(self, publicacion_id: UUID, user_id: UUID):
        """
        Metodo para eliminar una publicación.

        El comportamiento depende del perfil del usuario:

        - ADMIN:
            Hace tambien Soft Delete, no conviene borrar definitivamente las publicaciones.

        - PROFESOR:
            La eliminación es lógica (soft delete), marcando la publicación como inactiva.

        - ALUMNO:
            No puede eliminar publicaciones.

        Args:
            publicacion_id (UUID):
                ID de la publicación a eliminar.

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            dict:
                Mensaje confirmando la eliminación.

        Raises:
            HTTPException:
                404 si la publicación no existe.
                403 si el usuario no tiene permisos.
                500 si ocurre un error interno.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        publicacion = self.publicacion_repo.get_by_id(publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        # 🔐 Permisos
        puede = self.permission.puede_eliminar_publicacion(usuario, publicacion)

        if not puede:
            raise HTTPException(403, "No autorizado para eliminar")

        # 🧹 Soft delete
        self.publicacion_repo.soft_delete(publicacion)

        self.session.commit()

        return {"detail": "Publicación desactivada correctamente"}
    
    def descargar_archivo(self, archivo_id: UUID, user_id: UUID):
        """
        Endpoint para generar una URL firmada de descarga de un archivo.

        Puede tratarse de:
        - archivo de publicación
        - archivo de entrega de tarea

        Se valida que el usuario tenga acceso a la materia
        antes de permitir la descarga.

        Control de acceso:

        - ADMIN:
            Puede descargar cualquier archivo.

        - PROFESOR:
            Puede descargar archivos de materias donde esté asignado.

        - ALUMNO:
            Puede descargar archivos de materias donde esté inscripto.
            Solo puede acceder a sus propias entregas.

        Args:
            archivo_id (UUID):
                ID del archivo almacenado.

            user:
                Usuario autenticado obtenido desde el token JWT.

            session (Session):
                Sesión de base de datos.

        Returns:
            dict:
                URL firmada temporal para descargar el archivo desde Supabase Storage.

        Raises:
            HTTPException:
                404 si el archivo no existe.
                403 si el usuario no tiene permisos.
                500 si ocurre un error interno.
        """

        usuario = self.session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        ruta = None
        publicacion = None
        entrega = None

        archivo_publicacion = self.archivo_publicacion_repo.get_by_id(archivo_id)

        if archivo_publicacion:
            publicacion = self.publicacion_repo.get_by_id(archivo_publicacion.publicacion_id)
            ruta = archivo_publicacion.ruta_archivo

        else:
            archivo_entrega = self.tarea_entregada_repo.get_by_id(archivo_id)
            if not archivo_entrega:
                raise HTTPException(404, "Archivo no encontrado")

            entrega = self.entrega_repo.get_by_id(archivo_entrega.entrega_id)
            if not entrega:
                raise HTTPException(404, "Entrega no encontrada")

            publicacion = self.publicacion_repo.get_by_id(entrega.publicacion_id)
            ruta = archivo_entrega.ruta_archivo

        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        if not self.permission.puede_descargar(usuario, publicacion, entrega):
            raise HTTPException(403, "No autorizado")

        signed_url = StorageService.generar_url_firmada(ruta, 600)

        return {"url": signed_url}